import math
from typing import List, Union
import numpy as np
import cupy as cp


def dot(A, B, gpu_out: bool = False, sync: bool = True):
    """ Applying the dot operator between A and B

    Args:
        A(np.array<np.complex>): the matrix A
        B(np.array<np.complex>): the matrix B
        gpu_out(bool): return result from GPU into CPU
        sync(bool): Whether sync mode of async mode

    Returns:
        np.array<np.complex>: A * B
    """
    assert (A.shape[1] == B.shape[0])

    # Data in GPU.
    gpu_A = cp.array(A) if type(A) is np.ndarray else A
    gpu_B = cp.array(B) if type(B) is np.ndarray else B

    gpu_result = cp.dot(gpu_A, gpu_B)

    if sync:
        cp.cuda.Device().synchronize()

    if gpu_out:
        return gpu_result.get()

    return gpu_result


tensor_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void tensorsingle(
        complex<float>* x, complex<float>* y, complex<float>* out,
        int cx, int ry, int cy, long long max_size
    ) {
        long long out_id = blockDim.x * blockIdx.x + threadIdx.x;
        if (out_id >= max_size){
            return;
        }
        int out_width = cx * cy;
        int x_id = (out_id/out_width)/ry * cx + (out_id%out_width) / cy;
        int y_id = (out_id/out_width)%ry * cy + (out_id%out_width) % cy;
        out[out_id] = x[x_id] * y[y_id];
    }
    ''', 'tensorsingle')


tensor_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void tensordouble(
        complex<double>* x, complex<double>* y, complex<double>* out,
        int cx, int ry, int cy, long long max_size
    ) {
        long long out_id = blockDim.x * blockIdx.x + threadIdx.x;
        if (out_id >= max_size){
            return;
        }
        int out_width = cx * cy;
        int x_id = (out_id/out_width)/ry * cx + (out_id%out_width) / cy;
        int y_id = (out_id/out_width)%ry * cy + (out_id%out_width) % cy;
        out[out_id] = x[x_id] * y[y_id];
    }
    ''', 'tensordouble')


def tensor(A, B, gpu_out: bool = False, sync: bool = True):
    """ Applying the tensor operator between A and B.

    Args:
        A(np.array<np.complex>): the matrix A
        B(np.array<np.complex>): the matrix B
        gpu_out(bool): return result from GPU into CPU
        sync(bool): Whether sync mode of async mode

    Returns:
        np.array<np.complex>: the tensor result A ⊗ B
    """
    # Data in GPU.
    gpu_A = cp.array(A) if type(A) is np.ndarray else A
    gpu_B = cp.array(B) if type(B) is np.ndarray else B

    row_a, row_b = A.shape[0], B.shape[0]
    col_a = 1 if A.ndim == 1 else A.shape[1]
    col_b = 1 if B.ndim == 1 else B.shape[1]

    gpu_result = cp.empty((row_a * row_b, col_a * col_b), dtype=A.dtype)
    core_number = gpu_result.size
    kernel_function = tensor_single_kernel if A.dtype == np.complex64 else tensor_double_kernel
    kernel_function(
        (math.ceil(core_number / 1024),),
        (min(1024, core_number),),
        (gpu_A, gpu_B, gpu_result, cp.int32(col_a), cp.int32(row_b), cp.int32(col_b), cp.longlong(gpu_result.size))
    )

    if sync:
        cp.cuda.Device().synchronize()

    if gpu_out:
        return gpu_result.get()

    return gpu_result


matrixt_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void matrix_tensorI_single(
        const complex<float>* A, complex<float>* out,
        int n, int m, int rx, int cx, long long max_size
    ) {
        long long tid = blockDim.x * blockIdx.x + threadIdx.x;
        if (tid > max_size){
            return;
        }
        long long x_id = tid/cx;
        long long y_id = (x_id/(rx*m))*(m*cx) + (tid%cx)*m + (x_id%(rx*m))%m;
        long long out_xid = (x_id%(rx*m))/m;
        long long out_yid = tid%cx;
        long long out_id = x_id*(cx*n*m) + y_id;
        out[out_id] = A[out_xid*cx + out_yid];
    }
    ''', 'matrix_tensorI_single')


matrixt_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void matrix_tensorI_double(
        const complex<double>* A, complex<double>* out,
        int n, int m, int rx, int cx, long long max_size
    ) {
        long long tid = blockDim.x * blockIdx.x + threadIdx.x;
        if (tid > max_size){
            return;
        }
        long long x_id = tid/cx;
        long long y_id = (x_id/(rx*m))*(m*cx) + (tid%cx)*m + (x_id%(rx*m))%m;
        long long out_xid = (x_id%(rx*m))/m;
        long long out_yid = tid%cx;
        long long out_id = x_id*(cx*n*m) + y_id;
        out[out_id] = A[out_xid*cx + out_yid];
    }
    ''', 'matrix_tensorI_double')


def MatrixTensorI(A, n, m, gpu_out: bool = False, sync: bool = True):
    """ Applying the Matrix Tensor operator to matrix A

    $$ A' = I^n \otimes A \otimes I^m $$

    Args:
        A(np.array<np.complex>): the matrix A
        n(int): the index of indentity
        m(int): the index of indentity
        gpu_out(bool): return result from GPU into CPU
        sync(bool): Whether sync mode of async mode

    Returns:
        np.array<np.complex>: the tensor result I^n ⊗ A ⊗ I^m
    """
    if n == 1 and m == 1:
        return A

    row_a, col_a = A.shape

    # Data in GPU.
    precision = A.dtype
    gpu_A = cp.array(A) if type(A) is np.ndarray else A

    gpu_result = cp.zeros((row_a * n * m, col_a * n * m), dtype=precision)
    core_number = gpu_A.size * n * m
    kernel_function = matrixt_single_kernel if A.dtype == np.complex64 else matrixt_double_kernel
    kernel_function(
        (math.ceil(core_number / 1024),),
        (min(1024, core_number),),
        (gpu_A, gpu_result, cp.int32(n), cp.int32(m), cp.int32(row_a), cp.int32(col_a), cp.longlong(gpu_result.size))
    )

    if sync:
        cp.cuda.Device().synchronize()

    if gpu_out:
        return gpu_result.get()

    return gpu_result


vectorp_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void vector_single_permutation(const complex<float>* x, complex<float>* y, int* mapping, int m) {
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        int xid = 0;
        int l = 0;
        for(int i = 0; i < m; i++){
            if ((i != m - 1) && ((mapping[i] + 1) == mapping[i+1])){
                l += 1;
            }else{
                xid |= ((tid >> (m - 1 - mapping[i])) & ((1 << (l + 1)) - 1)) << (m - 1 - i);
                l = 0;
            }
        }
        y[tid] = x[xid];
    }
    ''', 'vector_single_permutation')


vectorp_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void vector_double_permutation(const complex<double>* x, complex<double>* y, int* mapping, int m) {
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        int xid = 0;
        int l = 0;
        for(int i = 0; i < m; i++){
            if ((i != m - 1) && ((mapping[i] + 1) == mapping[i+1])){
                l += 1;
            }else{
                xid |= ((tid >> (m - 1 - mapping[i])) & ((1 << (l + 1)) - 1)) << (m - 1 - i);
                l = 0;
            }
        }
        y[tid] = x[xid];
    }
    ''', 'vector_double_permutation')


def VectorPermutation(A, mapping, changeInput: bool = False, gpu_out: bool = False, sync: bool = True):
    """ permutaion A with mapping, inplace

    Args:
        A(np.array<np.complex>): the matrix A.
        mapping(np.array<int>): the qubit mapping.
        changeInput(bool): whether changes in A.
        gpu_out(bool): return result from GPU.
        sync(bool): Whether sync mode of async mode

    Returns:
        np.array<np.complex>: the result of Permutation
    """
    row_a, n = A.shape[0], mapping.shape[0]
    if not row_a == 1 << n:
        raise IndexError("Indices do not match!")

    if mapping.dtype == np.int64:
        mapping = mapping.astype(np.int32)

    # data in GPU
    gpu_A = cp.array(A) if type(A) is np.ndarray else A
    gpu_mapping = cp.array(mapping)
    gpu_result = cp.empty_like(gpu_A)
    core_number = gpu_result.size
    kernel_function = vectorp_single_kernel if A.dtype == np.complex64 else vectorp_double_kernel
    kernel_function(
        (math.ceil(core_number / 1024),),
        (min(1024, core_number),),
        (gpu_A, gpu_result, gpu_mapping, cp.int32(n))
    )

    if sync:
        cp.cuda.Device().synchronize()

    if changeInput:
        A[:] = gpu_result.get() if type(A) is np.ndarray else gpu_result
        del gpu_result
        return

    if gpu_out:
        return gpu_result.get()

    return gpu_result


matrixp_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void matrix_single_permutation(const complex<float>* x, complex<float>* y, int* mapping, int m) {
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        int len = 1 << m;
        int rx = tid/len;
        int cx = tid%len;
        int rtemp = 0;
        int ctemp = 0;
        int l = 1;
        for(int i = 0; i < m; i++){
            if ((i != m - 1) && ((mapping[i] | 1) == mapping[i+1])){
                l = (l << 1) | 1;
            }else{
                rtemp |= ((rx >> (m - 1 - mapping[i])) & l) << (m - 1 - i);
                ctemp |= ((cx >> (m - 1 - mapping[i])) & l) << (m - 1 - i);
                l = 1;
            }
        }
        y[tid] = x[rtemp*len + ctemp];
    }
    ''', 'matrix_single_permutation')


matrixp_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void matrix_double_permutation(const complex<double>* x, complex<double>* y, int* mapping, int m) {
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        int len = 1 << m;
        int rx = tid/len;
        int cx = tid%len;
        int rtemp = 0;
        int ctemp = 0;
        int l = 1;
        for(int i = 0; i < m; i++){
            if ((i != m - 1) && ((mapping[i] | 1) == mapping[i+1])){
                l = (l << 1) | 1;
            }else{
                rtemp |= ((rx >> (m - 1 - mapping[i])) & l) << (m - 1 - i);
                ctemp |= ((cx >> (m - 1 - mapping[i])) & l) << (m - 1 - i);
                l = 1;
            }
        }
        y[tid] = x[rtemp*len + ctemp];
    }
    ''', 'matrix_double_permutation')


def MatrixPermutation(A, mapping, changeInput: bool = False, gpu_out: bool = False, sync: bool = True):
    """ permute mat with mapping, inplace

    Args:
        A(np.array<np.complex>): the matrix A.
        mapping(np.array<int>): the qubit mapping.
        changeInput(bool): whether changes in A.
        gpu_out(bool): return result from GPU.
        sync(bool): Whether sync mode of async mode
    """
    row_a, n = A.shape[0], mapping.shape[0]
    if not row_a == 1 << n:
        raise IndexError("Indices do not match!")

    if mapping.dtype == np.int64:
        mapping = mapping.astype(np.int32)

    # data in GPU
    gpu_A = cp.array(A) if type(A) is np.ndarray else A
    gpu_mapping = cp.array(mapping)
    gpu_result = cp.empty_like(gpu_A)
    core_number = gpu_result.size
    kernel_function = matrixp_single_kernel if A.dtype == np.complex64 else matrixp_double_kernel
    kernel_function(
        (math.ceil(core_number / 1024),),
        (min(1024, core_number),),
        (gpu_A, gpu_result, gpu_mapping, cp.int32(n))
    )

    if sync:
        cp.cuda.Device().synchronize()

    if changeInput:
        A[:, :] = gpu_result.get() if type(A) is np.ndarray else gpu_result
        del gpu_result
        return

    if gpu_out:
        return gpu_result.get()

    return gpu_result


matrix_dot_vector_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void matrix_dot_vector_single(
        const complex<float>* mat,
        int mat_bit,
        int mat_len,
        complex<float>* vec,
        int* affect_args,
        int* aff_argsorts
    ){
        long long tid = blockDim.x * blockIdx.x + threadIdx.x;
        long long other = tid & ((1 << aff_argsorts[0]) - 1);
        long long gw = tid >> aff_argsorts[0] << (aff_argsorts[0] + 1);
        for(int i = 1; i < mat_bit; i++){
            other += gw & ((1 << aff_argsorts[i]) - (1 << aff_argsorts[i - 1]));
            gw = gw >> aff_argsorts[i] << (aff_argsorts[i] + 1);
        }
        other += gw;

        long long *mat_idx = new long long[mat_len];
        mat_idx[0] = other;
        for (int i = 1; i < mat_len; i++){
            long long temp_midx = 0;
            for(int k = 0; k < mat_bit; k++){
                if (i & (1 << k)){
                    temp_midx += 1 << affect_args[mat_bit - 1 - k];
                }
            }
            mat_idx[i] = temp_midx + other;
        }

        complex<float> *temp_val = new complex<float>[mat_len];
        for(int col = 0; col < mat_len; col++){
            temp_val[col] = 0;
            for(int row = 0; row < mat_len; row++){
                temp_val[col] += mat[col*mat_len + row] * vec[mat_idx[row]];
            }
        }

        for(int i = 1; i < mat_len; i++){
            vec[mat_idx[i]] = temp_val[i];
        }
    }
    ''', 'matrix_dot_vector_single')


matrix_dot_vector_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void matrix_dot_vector_double(
        const complex<double>* mat,
        const int mat_bit,
        const int mat_len,
        complex<double>* vec,
        int* affect_args,
        int* aff_argsorts
    ){
        long long tid = blockDim.x * blockIdx.x + threadIdx.x;
        long long other = tid & ((1 << aff_argsorts[0]) - 1);
        long long gw = tid >> aff_argsorts[0] << (aff_argsorts[0] + 1);
        for(int i = 1; i < mat_bit; i++){
            other += gw & ((1 << aff_argsorts[i]) - (1 << aff_argsorts[i - 1]));
            gw = gw >> aff_argsorts[i] << (aff_argsorts[i] + 1);
        }
        other += gw;

        long long *mat_idx = new long long[mat_len];
        mat_idx[0] = other;
        for (int i = 1; i < mat_len; i++){
            int temp_midx = 0;
            for(int k = 0; k < mat_bit; k++){
                if (i & (1 << k)){
                    temp_midx += 1 << affect_args[mat_bit - 1 - k];
                }
            }
            mat_idx[i] = temp_midx + other;
        }

        complex<double> *temp_val = new complex<double>[mat_len];
        for(int col = 0; col < mat_len; col++){
            temp_val[col] = 0;
            for(int row = 0; row < mat_len; row++){
                temp_val[col] += mat[col*mat_len + row] * vec[mat_idx[row]];
            }
        }

        for(int i = 1; i < mat_len; i++){
            vec[mat_idx[i]] = temp_val[i];
        }
    }
    ''', 'matrix_dot_vector_double')


def matrix_dot_vector(
    vec: Union[np.ndarray, cp.ndarray],
    vec_bit: int,
    mat: Union[np.ndarray, cp.ndarray],
    mat_args: List[int],
    sync: bool = True
):
    """ Dot the quantum gate's matrix and qubits'state vector, depending on the target qubits of gate.

    Args:
        vec (np.ndarray): The state vector of qubits
        vec_bit (int): The number of qubits
        mat (np.ndarray): The 2D numpy array, represent the quantum gate's matrix
        mat_args (List[int]): The qubits' indexes of matrix.
        sync(bool): Whether sync mode of async mode.

    Returns:
        np.ndarray: updated state vector
    """
    # Matrix property
    mat_bit = np.int32(len(mat_args))
    mat_length = np.int32(2 ** mat_bit)
    assert vec_bit >= mat_bit, "Vector length should larger than matrix."

    if vec_bit == mat_bit:
        return dot(mat, vec, sync=sync)

    # GPU preparation
    task_number = 1 << (vec_bit - mat_bit)
    thread_per_block = min(256, task_number)
    block_num = task_number // thread_per_block

    sorted_mat_args = mat_args.copy()
    sorted_mat_args.sort()
    mat_args = cp.array(mat_args, dtype=np.int32)
    sorted_mat_args = cp.array(sorted_mat_args, dtype=np.int32)

    # Vector, Matrix preparation
    if isinstance(vec, np.ndarray):
        vec = cp.array(vec, dtype=vec.dtype)

    if isinstance(mat, np.ndarray):
        mat = cp.array(mat, dtype=mat.dtype)

    # Start GPU kernel function
    kernel_function = matrix_dot_vector_single_kernel if vec.dtype == np.complex64 else matrix_dot_vector_double_kernel
    kernel_function(
        (block_num,),
        (thread_per_block,),
        (mat, mat_bit, mat_length, vec, mat_args, sorted_mat_args)
    )

    if sync:
        cp.cuda.Device().synchronize()


matrix_dot_matrix_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void matrix_dot_matrix_single(
        const complex<float>* mat_g,
        int gate_bit,
        int tgate_bit,
        int gate_len,
        complex<float>* mat_u,
        int mat_bit,
        int mat_len,
        int* affect_args,
        int* aff_argsorts,
        long long based
    ){
        long long tid = blockDim.x * blockIdx.x + threadIdx.x;
        long long mat_width = (long long)1 << (mat_bit - gate_bit);
        long long xid = tid / mat_width;
        long long yid = tid % mat_width;

        long long x_other = xid & ((1 << aff_argsorts[0]) - 1);
        long long y_other = yid & ((1 << aff_argsorts[0]) - 1);
        long long x_gw = xid >> aff_argsorts[0] << (aff_argsorts[0] + 1);
        long long y_gw = yid >> aff_argsorts[0] << (aff_argsorts[0] + 1);
        for(int i = 1; i < gate_bit; i++){
            x_other += x_gw & ((1 << aff_argsorts[i]) - (1 << aff_argsorts[i - 1]));
            x_gw = x_gw >> aff_argsorts[i] << (aff_argsorts[i] + 1);
            y_other += y_gw & ((1 << aff_argsorts[i]) - (1 << aff_argsorts[i - 1]));
            y_gw = y_gw >> aff_argsorts[i] << (aff_argsorts[i] + 1);
        }
        x_other += x_gw;
        y_other += y_gw;

        long long *x_mat_idx = new long long[gate_len];
        long long *y_mat_idx = new long long[gate_len];
        x_mat_idx[0] = x_other + based;
        y_mat_idx[0] = y_other + based;
        for (int i = 1; i < gate_len; i++){
            long long temp_midx = 0;
            for(int k = 0; k < (1 << tgate_bit); k++){
                if (i & (1 << k)){
                    temp_midx += 1 << affect_args[tgate_bit - 1 - k];
                }
            }
            x_mat_idx[i] = temp_midx + x_mat_idx[0];
            y_mat_idx[i] = temp_midx + y_mat_idx[0];
        }

        complex<float> *temp_val = new complex<float>[gate_len * gate_len];
        for(int col = 0; col < gate_len * gate_len; col++){
            int temp_ix_idx = col / gate_len;
            int temp_iy_idx = col % gate_len;

            temp_val[col] = (complex<float>)0;
            for(int row = 0; row < gate_len; row++){
                temp_val[col] += mat_u[x_mat_idx[row]*mat_len + y_mat_idx[temp_iy_idx]] * mat_g[temp_ix_idx*gate_len + row];
            }
        }

        for(int i_map = 0; i_map < gate_len; i_map++){
            for(int j_map = 0; j_map < gate_len; j_map++){
            mat_u[x_mat_idx[i_map]*mat_len + y_mat_idx[j_map]] = temp_val[i_map*gate_len + j_map];
            }
        }
    }
    ''', 'matrix_dot_matrix_single')


matrix_dot_matrix_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void matrix_dot_matrix_double(
        const complex<double>* mat_g,
        int gate_bit,
        int tgate_bit,
        int gate_len,
        complex<double>* mat_u,
        int mat_bit,
        int mat_len,
        int* affect_args,
        int* aff_argsorts,
        long long based
    ){
        long long tid = blockDim.x * blockIdx.x + threadIdx.x;
        long long mat_width = (long long)1 << (mat_bit - gate_bit);
        long long xid = tid / mat_width;
        long long yid = tid % mat_width;

        long long x_other = xid & (((long long)1 << aff_argsorts[0]) - 1);
        long long y_other = yid & (((long long)1 << aff_argsorts[0]) - 1);
        long long x_gw = xid >> aff_argsorts[0] << (aff_argsorts[0] + 1);
        long long y_gw = yid >> aff_argsorts[0] << (aff_argsorts[0] + 1);
        for(int i = 1; i < gate_bit; i++){
            x_other += x_gw & (((long long)1 << aff_argsorts[i]) - ((long long)1 << aff_argsorts[i - 1]));
            x_gw = x_gw >> aff_argsorts[i] << (aff_argsorts[i] + 1);
            y_other += y_gw & (((long long)1 << aff_argsorts[i]) - ((long long)1 << aff_argsorts[i - 1]));
            y_gw = y_gw >> aff_argsorts[i] << (aff_argsorts[i] + 1);
        }
        x_other += x_gw;
        y_other += y_gw;

        long long *x_mat_idx = new long long[gate_len];
        long long *y_mat_idx = new long long[gate_len];
        x_mat_idx[0] = x_other + based;
        y_mat_idx[0] = y_other + based;
        for (int i = 1; i < gate_len; i++){
            long long temp_midx = 0;
            for(int k = 0; k < (1 << tgate_bit); k++){
                if (i & (1 << k)){
                    temp_midx += 1 << affect_args[tgate_bit - 1 - k];
                }
            }
            x_mat_idx[i] = temp_midx + x_mat_idx[0];
            y_mat_idx[i] = temp_midx + y_mat_idx[0];
        }

        complex<double> *temp_val = new complex<double>[gate_len * gate_len];
        for(int col = 0; col < gate_len * gate_len; col++){
            int temp_ix_idx = col / gate_len;
            int temp_iy_idx = col % gate_len;

            temp_val[col] = (complex<double>)0;
            for(int row = 0; row < gate_len; row++){
                temp_val[col] += mat_u[x_mat_idx[row]*mat_len + y_mat_idx[temp_iy_idx]] * mat_g[temp_ix_idx*gate_len + row];
            }
        }

        for(int i_map = 0; i_map < gate_len; i_map++){
            for(int j_map = 0; j_map < gate_len; j_map++){
                mat_u[x_mat_idx[i_map]*mat_len + y_mat_idx[j_map]] = temp_val[i_map*gate_len + j_map];
            }
        }
    }
    ''', 'matrix_dot_matrix_double')


def matrix_dot_matrix(
    mat_u: Union[np.ndarray, cp.ndarray],
    mat_g: Union[np.ndarray, cp.ndarray],
    control_args: np.ndarray = None,
    target_args: np.ndarray = None,
    sync: bool = True
):
    """ Dot the quantum gate's matrix and qubits'state vector, depending on the target qubits of gate.

    Args:
        vec (np.ndarray): The state vector of qubits
        vec_bit (int): The number of qubits
        mat (np.ndarray): The 2D numpy array, represent the quantum gate's matrix
        mat_args (List[int]): The qubits' indexes of matrix.
        sync(bool): Whether sync mode of async mode.

    Returns:
        np.ndarray: updated state vector
    """
    # Matrix property
    # Step 1: Calculate mat_bit and vec_bit
    mat_bit = int(np.log2(mat_u.shape[0]))
    mat_length = mat_u.shape[0]
    len_c = 0 if control_args is None else len(control_args)
    len_t = 0 if target_args is None else len(target_args)
    gate_bit = len_c + len_t
    assert mat_bit >= gate_bit, "Vector length should larger than matrix."
    assert mat_length == 1 << mat_bit, "Matrix should be unitary and with [2^n, 2^n] shape."

    # Vector, Matrix preparation
    if isinstance(mat_u, np.ndarray):
        mat_u = cp.array(mat_u, dtype=mat_u.dtype)

    if isinstance(mat_g, np.ndarray):
        mat_g = cp.array(mat_g, dtype=mat_g.dtype)

    if mat_bit == gate_bit and len_c == 0:
        cp.dot(mat_g, mat_u, out=mat_u)
        return

    # Step 2: Get fixed index of vector by control indexes
    based_idx = 0
    if control_args is not None:
        for carg_idx in control_args:
            based_idx += 1 << carg_idx

    # Step 3: sorted target qubit indexes
    gate_args = cp.array(target_args, dtype=cp.int32)
    sorted_gate_args = np.append(control_args, target_args) if control_args is not None else target_args
    sorted_gate_args = cp.array(sorted_gate_args, dtype=cp.int32)
    sorted_gate_args.sort()

    # Step 4: start GPU Kernel function
    task_number = 1 << (2 * (mat_bit - gate_bit))
    thread_per_block = min(256, task_number)
    block_num = task_number // thread_per_block
    kernel_function = matrix_dot_matrix_single_kernel if mat_g.dtype == np.complex64 else matrix_dot_matrix_double_kernel
    kernel_function(
        (block_num,),
        (thread_per_block,),
        (
            mat_g, gate_bit, len_t, cp.int32(1 << len_t),
            mat_u, mat_bit, mat_length,
            gate_args, sorted_gate_args, cp.longlong(based_idx)
        )
    )

    if sync:
        cp.cuda.Device().synchronize()


combine_array_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void combine_array_single(
        const complex<float>* vec,
        complex<float>* out,
        int block_size,
        int max_size
    ){
        long long tid = blockDim.x * blockIdx.x + threadIdx.x;
        long long s_idx = tid * block_size;
        if (tid >= max_size){
            return;
        }

        out[tid] = abs(vec[s_idx]) * abs(vec[s_idx]);
        for(int i = 1; i < block_size; i++){
            out[tid] += abs(vec[s_idx+i]) * abs(vec[s_idx+i]);
        }
    }
    ''', 'combine_array_single')


combine_array_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void combine_array_double(
        const complex<double>* vec,
        complex<double>* out,
        int block_size,
        int max_size
    ){
        long long tid = blockDim.x * blockIdx.x + threadIdx.x;
        long long s_idx = tid * block_size;
        if (tid >= max_size){
            return;
        }

        out[tid] = abs(vec[s_idx]) * abs(vec[s_idx]);
        for(int i = 1; i < block_size; i++){
            out[tid] += abs(vec[s_idx+i]) * abs(vec[s_idx+i]);
        }
    }
    ''', 'combine_array_double')


def array_combination(
    state_vector, sv_qubits: int, block_qubits: int, sync: bool = True
):
    # data in GPU
    gpu_sv = cp.array(state_vector) if type(state_vector) is np.ndarray else state_vector
    cmb_sv = cp.empty(1 << (sv_qubits - block_qubits), dtype=gpu_sv.dtype)
    kernel_funcs = combine_array_double_kernel if gpu_sv.dtype == cp.complex128 else combine_array_single_kernel

    task_number = 1 << (sv_qubits - block_qubits)
    thread_per_block = min(256, task_number)
    block_num = task_number // thread_per_block
    kernel_funcs(
        (block_num,),
        (thread_per_block,),
        (gpu_sv, cmb_sv, cp.int32(block_qubits), cp.int32(task_number))
    )

    if sync:
        cp.cuda.Device().synchronize()

    return cmb_sv


vector_sampling_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void vector_sampling(const float* cdf, int* shots, float* rand_vals, int qubits, int shot_num) {
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        if (tid >= shot_num){
            return;
        }

        float target_val = rand_vals[tid];
        int cdf_idx = 1 << (qubits - 1);
        int step = qubits - 2;
        float curr_val;
        while (step >= 0){
            curr_val = cdf[cdf_idx];
            if (curr_val == target_val){
                break;
            }else if(curr_val < target_val){
                cdf_idx += (1 << step);
            }else{
                cdf_idx -= (1 << step);
            }
            step--;
        }

        if (step == -1){
            if (cdf[cdf_idx] < target_val){
                cdf_idx += 1;
            }else if(cdf[cdf_idx - 1] > target_val){
                cdf_idx -= 1;
            }
        }
        shots[tid] = cdf_idx;
    }
    ''', 'vector_sampling')


partial_sampling_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void partial_sampling(int* shots, int* target_qubits, int q_num, int shot_num, int tqubit_num) {
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        if (tid >= shot_num){
            return;
        }

        int curr_shot = shots[tid];
        int related_shot = 0;
        for (int i = 0; i < tqubit_num; i++){
            related_shot <<= 1;
            if ((curr_shot & (1 << (q_num - target_qubits[i] - 1))) > 0){
                related_shot += 1;
            }
        }

        shots[tid] = related_shot;
    }
    ''', 'partial_sampling')


large_partial_sampling_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void large_partial_sampling(long long* shots, int* target_qubits, int q_num, int shot_num, int tqubit_num) {
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        if (tid >= shot_num){
            return;
        }

        long long curr_shot = shots[tid];

        long long related_shot = 0;
        for (int i = 0; i < tqubit_num; i++){
            related_shot <<= 1;
            if ((curr_shot & ((long long)1 << (q_num - target_qubits[i] - 1))) > 0){
                related_shot += 1;
            }
        }

        shots[tid] = related_shot;
    }
    ''', 'large_partial_sampling')


def sv_sampling(A, shots: int, num_qubits: int, target_qubits: list = None, sync: bool = True, seed: int = -1):
    """ permute mat with mapping, inplace

    Args:
        A(cp.array<float32>): the cdf vector A.
        shots(int): The number of sample.
        num_qubits(int): The number of quantum qubits.
        target_qubits (list): The List of target sample qubits.
        sync(bool): Whether sync mode of async mode
    """
    if seed != -1:
        cp.random.seed(seed)

    # data in GPU
    gpu_A = cp.array(A) if type(A) is np.ndarray else A
    shot_list = cp.empty(shots, dtype=np.int32)
    random_val_list = cp.random.rand(shots, dtype=cp.float32)
    if not cp.isclose(gpu_A[-1], 1):
        random_val_list = random_val_list * gpu_A[-1]

    vector_sampling_kernel(
        (math.ceil(shots / 1024),),
        (min(1024, shots),),
        (gpu_A, shot_list, random_val_list, num_qubits, shots)
    )

    if target_qubits is not None:
        tq_num = len(target_qubits)
        partial_sampling_kernel(
            (math.ceil(shots / 1024),),
            (min(1024, shots),),
            (shot_list, target_qubits, num_qubits, shots, tq_num)
        )

    if sync:
        cp.cuda.Device().synchronize()

    return shot_list


def sv_sampling_for_all_qubits(A, shots: int, num_qubits: int, sync: bool = True, seed: int = -1):
    """ permute mat with mapping, inplace

    Args:
        A(cp.array<float32>): the cdf vector A.
        shots(int): The number of sample.
        num_qubits(int): The number of quantum qubits.
        sync(bool): Whether sync mode of async mode
    """
    if seed != -1:
        cp.random.seed(seed)

    # data in GPU
    gpu_A = cp.array(A) if type(A) is np.ndarray else A
    shot_list = cp.empty(shots, dtype=np.int32)
    random_val_list = cp.random.rand(shots, dtype=cp.float32)
    if not cp.isclose(gpu_A[-1], 1):
        random_val_list = random_val_list * gpu_A[-1]

    vector_sampling_kernel(
        (math.ceil(shots / 1024),),
        (min(1024, shots),),
        (gpu_A, shot_list, random_val_list, num_qubits, shots)
    )

    if sync:
        cp.cuda.Device().synchronize()

    return shot_list


def partial_sv_sampling(
    partial_prob, state_vector,
    shots: int, num_qubits: int, block_qubits: int,
    target_qubits: list = None, sync: bool = True, seed: int = -1
):
    """ permute mat with mapping, inplace

    Args:
        A(cp.array<float32>): the cdf vector A.
        shots(int): The number of sample.
        num_qubits(int): The number of quantum qubits.
        target_qubits (list): The List of target sample qubits.
        sync(bool): Whether sync mode of async mode
    """
    if seed != -1:
        cp.random.seed(seed)

    # data in GPU
    gpu_sv = cp.array(state_vector) if type(state_vector) is np.ndarray else state_vector
    shot_list = cp.empty(shots, dtype=np.int32)
    random_val_list = cp.random.rand(shots, dtype=cp.float32)
    if not cp.isclose(partial_prob[-1], 1):
        random_val_list = random_val_list * partial_prob[-1]

    vector_sampling_kernel(
        (math.ceil(shots / 1024),),
        (min(1024, shots),),
        (partial_prob, shot_list, random_val_list, num_qubits - block_qubits, shots)
    )

    block_dim = 1 << block_qubits
    new_shot_list = cp.empty(shots, dtype=cp.int64)
    for idx in range(shots):
        sval = cp.int64(shot_list[idx].get())
        block_prob = cp.cumsum(
            cp.square(cp.abs(gpu_sv[block_dim * sval: block_dim * (sval + 1)])),
            dtype=cp.float32
        )
        rval = cp.random.rand(1, dtype=cp.float32) * block_prob[-1]
        for bidx, bprob in enumerate(block_prob):
            if bprob >= rval:
                new_shot_list[idx] = block_dim * sval + bidx
                break

    if target_qubits is not None:
        tq_num = len(target_qubits)
        large_partial_sampling_kernel(
            (math.ceil(shots / 1024),),
            (min(1024, shots),),
            (new_shot_list, target_qubits, num_qubits, shots, tq_num)
        )

    if sync:
        cp.cuda.Device().synchronize()

    return new_shot_list


def partial_sv_sampling_for_all_qubits(
    partial_prob,
    state_vector,
    shots: int,
    num_qubits: int,
    block_qubits: int,
    sync: bool = True,
    seed: int = -1,
):
    """ permute mat with mapping, inplace

    Args:
        partial_prob(cp.array<float32>): the cdf of state vector with block qubits.
        state_vector(cp.array<complex128>): The State Vector.
        shots(int): The number of sample.
        num_qubits(int): The number of quantum qubits.
        block_qubits(int): The number of block qubits.
        sync(bool): Whether sync mode of async mode
    """
    if seed != -1:
        cp.random.seed(seed)

    # data in GPU
    gpu_sv = cp.array(state_vector) if type(state_vector) is np.ndarray else state_vector
    shot_list = cp.empty(shots, dtype=np.int32)
    random_val_list = cp.random.rand(shots, dtype=cp.float32)
    if not cp.isclose(partial_prob[-1], 1):
        random_val_list = random_val_list * partial_prob[-1]

    vector_sampling_kernel(
        (math.ceil(shots / 1024),),
        (min(1024, shots),),
        (partial_prob, shot_list, random_val_list, num_qubits - block_qubits, shots)
    )

    block_dim = 1 << block_qubits
    new_shot_list = cp.empty(shots, dtype=cp.int64)
    for idx in range(shots):
        sval = cp.int64(shot_list[idx].get())
        block_prob = cp.cumsum(
            cp.square(cp.abs(gpu_sv[block_dim * sval: block_dim * (sval + 1)])),
            dtype=cp.float32
        )
        rval = cp.random.rand(1, dtype=cp.float32) * block_prob[-1]
        for bidx, bprob in enumerate(block_prob):
            if bprob > rval:
                new_shot_list[idx] = block_dim * sval + bidx
                break

    if sync:
        cp.cuda.Device().synchronize()

    return new_shot_list


partial_state_vector_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void partial_statevector(
        const double* probs, double* part_probs, int* target_qubits, int* sorted_tq, int qubit_num, int tqubit_num
    ){
        int tid = blockDim.x * blockIdx.x + threadIdx.x;
        if (tid >= (1 << qubit_num)){
            return;
        }

        int related_idx = 0;
        for (int i = 0; i < tqubit_num; i++){
            related_idx <<= 1;
            int target_bit_idx = qubit_num - target_qubits[i] - 1;
            if ((tid & (1 << target_bit_idx)) > 0){
                related_idx += 1;
            }
        }

        int related_tidx = tid;
        for (int i = 0; i < tqubit_num; i++){
            int curr_stq = qubit_num - sorted_tq[i] - 1;
            int less_item = related_tidx & ((1 << curr_stq) - 1);
            related_tidx = (related_tidx >> (curr_stq + 1) << curr_stq) | less_item;
        }
        part_probs[related_idx * (1 << (qubit_num - tqubit_num)) + related_tidx] = probs[tid];
    }
    ''', 'partial_statevector')


def sv_probability(A: cp.ndarray, num_qubits: int, target_qubits: cp.ndarray, sync: bool = True):
    prob_sv = cp.square(cp.abs(A))
    sum_prob_sv = cp.sum(prob_sv)

    if not cp.isclose(sum_prob_sv, 1):
        prob_sv /= sum_prob_sv

    partial_prob_sv = cp.zeros(
        (1 << target_qubits.size, 1 << (num_qubits - target_qubits.size)), dtype=prob_sv.dtype
    )
    sorted_tqs = cp.sort(target_qubits).astype(cp.int32)
    cores, tq_num = A.size, len(target_qubits)
    partial_state_vector_kernel(
        (math.ceil(cores / 1024),),
        (min(1024, cores),),
        (prob_sv, partial_prob_sv, target_qubits, sorted_tqs, num_qubits, tq_num)
    )
    partial_prob_sv = cp.sum(partial_prob_sv, axis=1)

    if sync:
        cp.cuda.Device().synchronize()

    if target_qubits is None:
        return prob_sv
    else:
        return partial_prob_sv


kernel_funcs = list(locals().keys())
for name in kernel_funcs:
    if name.endswith("kernel"):
        locals()[name].compile()
