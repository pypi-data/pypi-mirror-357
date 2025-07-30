import cupy as cp
import numpy as np
import random


__outward_functions = [
    "diagonal_targ",
    "diagonal_targs",
    "normal_targ",
    "normal_targs",
    "control_targ",
    "diagonal_ctargs",
    "control_ctargs",
    "control_cctarg",
    "normal_ctargs",
    "ctrl_normal_targs",
    "normal_normal_targs",
    "diagonal_normal_targs",
    "swap_targ",
    "reverse_targ",
    "reverse_ctargs",
    "reverse_targs",
    "swap_targs",
    "reverse_more",
    "diagonal_more",
    "swap_tmore",
    "apply_rccxgate",
    "measured_prob_calculate",
    "apply_measuregate",
    "apply_resetgate",
    "apply_multi_control_targ_gate",
    "apply_multi_control_targs_gate"
]


DEFAULT_BLOCK_NUM = 256
MEASURED_PRE_ADDED = 5


Diagonal_Multiply_targ_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Diagonal2x2Multiply(int parg, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _0 = (label >> parg << (parg + 1)) + (label & (offset - 1));
        long long _1 = _0 +  offset;

        vec[_0] = vec[_0]*mat[0];
        vec[_1] = vec[_1]*mat[3];
    }
    ''', 'Diagonal2x2Multiply')


Diagonal_Multiply_targ_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Diagonal2x2Multiply(int parg, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _0 = (label >> parg << (parg + 1)) + (label & (offset - 1));
        long long _1 = _0 +  offset;

        vec[_0] = vec[_0]*mat[0];
        vec[_1] = vec[_1]*mat[3];
    }
    ''', 'Diagonal2x2Multiply')


Diagonal_Multiply_targs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Diagonal4x4Multiply(int high, int low, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _1 + offset2;

        vec[_0] = vec[_0]*mat[0];
        vec[_1] = vec[_1]*mat[5];
        vec[_2] = vec[_2]*mat[10];
        vec[_3] = vec[_3]*mat[15];
    }
    ''', 'Diagonal4x4Multiply')


Diagonal_Multiply_targs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Diagonal4x4Multiply(int high, int low, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _1 + offset2;

        vec[_0] = vec[_0]*mat[0];
        vec[_1] = vec[_1]*mat[5];
        vec[_2] = vec[_2]*mat[10];
        vec[_3] = vec[_3]*mat[15];
    }
    ''', 'Diagonal4x4Multiply')


RDiagonal_Multiply_targs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void RDiagonal4x4Multiply(int high, int low, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _1 + offset2;

        complex<float> temp_0 = vec[_0];
        complex<float> temp_1 = vec[_1];
        vec[_0] = vec[_3]*mat[3];
        vec[_1] = vec[_2]*mat[6];
        vec[_2] = temp_1*mat[9];
        vec[_3] = temp_0*mat[12];
    }
    ''', 'RDiagonal4x4Multiply')


RDiagonal_Multiply_targs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void RDiagonal4x4Multiply(int high, int low, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _1 + offset2;

        complex<double> temp_0 = vec[_0];
        complex<double> temp_1 = vec[_1];
        vec[_0] = vec[_3]*mat[3];
        vec[_1] = vec[_2]*mat[6];
        vec[_2] = temp_1*mat[9];
        vec[_3] = temp_0*mat[12];
    }
    ''', 'RDiagonal4x4Multiply')


Based_InnerProduct_targ_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Based2x2InnerProduct(int parg, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _0 = (label >> parg << (parg + 1)) + (label & (offset - 1));
        long long _1 = _0 +  offset;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2] + vec[_1]*mat[3];
    }
    ''', 'Based2x2InnerProduct')


Based_InnerProduct_targ_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Based2x2InnerProduct(int parg, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _0 = (label >> parg << (parg + 1)) + (label & (offset - 1));
        long long _1 = _0 +  offset;

        complex<double> temp_0 = complex<double>(vec[_0]);
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2] + vec[_1]*mat[3];
    }
    ''', 'Based2x2InnerProduct')


Based_InnerProduct_targs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Based4x4InnerProduct(int t0, int t1, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << t0;
        const long long offset2 = (long long)1 << t1;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw=0, _0=0;

        if (t0 > t1){
            gw = label >> t1 << (t1 + 1);
            _0 = (gw >> t0 << (t0 + 1)) + (gw & (offset1 - offset2)) + (label & mask2);
        }
        else{
            gw = label >> t0 << (t0 + 1);
            _0 = (gw >> t1 << (t1 + 1)) + (gw & (offset2 - offset1)) + (label & mask1);
        }

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _1 + offset2;

        complex<float> temp_0 = vec[_0], temp_1 = vec[_1], temp_2 = vec[_2];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1] + vec[_2]*mat[2] + vec[_3]*mat[3];
        vec[_1] = temp_0*mat[4] + vec[_1]*mat[5] + vec[_2]*mat[6] + vec[_3]*mat[7];
        vec[_2] = temp_0*mat[8] + temp_1*mat[9] + vec[_2]*mat[10] + vec[_3]*mat[11];
        vec[_3] = temp_0*mat[12] + temp_1*mat[13] + temp_2*mat[14] + vec[_3]*mat[15];
    }
    ''', 'Based4x4InnerProduct')


Based_InnerProduct_targs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Based4x4InnerProduct(int t0, int t1, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << t0;
        const long long offset2 = (long long)1 << t1;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw=0, _0=0;

        if (t0 > t1){
            gw = label >> t1 << (t1 + 1);
            _0 = (gw >> t0 << (t0 + 1)) + (gw & (offset1 - offset2)) + (label & mask2);
        }
        else{
            gw = label >> t0 << (t0 + 1);
            _0 = (gw >> t1 << (t1 + 1)) + (gw & (offset2 - offset1)) + (label & mask1);
        }

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _1 + offset2;

        complex<double> temp_0 = vec[_0], temp_1 = vec[_1], temp_2 = vec[_2];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1] + vec[_2]*mat[2] + vec[_3]*mat[3];
        vec[_1] = temp_0*mat[4] + vec[_1]*mat[5] + vec[_2]*mat[6] + vec[_3]*mat[7];
        vec[_2] = temp_0*mat[8] + temp_1*mat[9] + vec[_2]*mat[10] + vec[_3]*mat[11];
        vec[_3] = temp_0*mat[12] + temp_1*mat[13] + temp_2*mat[14] + vec[_3]*mat[15];
    }
    ''', 'Based4x4InnerProduct')


Controlled_Multiply_targ_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled2x2Multiply(int parg, const complex<float> val, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _1 = (label >> parg << (parg + 1)) + offset + (label & (offset - 1));

        vec[_1] = vec[_1]*val;
    }
    ''', 'Controlled2x2Multiply')


Controlled_Multiply_targ_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled2x2Multiply(int parg, const complex<double> val, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _1 = (label >> parg << (parg + 1)) + offset + (label & (offset - 1));

        vec[_1] = vec[_1]*val;
    }
    ''', 'Controlled2x2Multiply')


Controlled_Multiply_ctargs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4Multiply(const complex<float>* mat, complex<float>* vec, int c_index, int t_index) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c = (long long)1 << c_index;
        const long long offset_t = (long long)1 << t_index;
        const long long mask_c = offset_c - 1;
        const long long mask_t = offset_t - 1;

        long long gw=0, _0=0;

        if (t_index > c_index){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c)) + (label & mask_c);
        }
        else
        {
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t)) + (label & mask_t);
        }

        long long _1 = _0 + offset_t;

        vec[_0] = vec[_0]*mat[0];
        vec[_1] = vec[_1]*mat[3];
    }
    ''', 'Controlled4x4Multiply')


Controlled_Multiply_ctargs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4Multiply(const complex<double>* mat, complex<double>* vec, int c_index, int t_index){
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c = (long long)1 << c_index;
        const long long offset_t = (long long)1 << t_index;
        const long long mask_c = offset_c - 1;
        const long long mask_t = offset_t - 1;

        long long gw=0, _0=0;

        if (t_index > c_index){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c)) + (label & mask_c);
        }
        else
        {
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t)) + (label & mask_t);
        }

        long long _1 = _0 + offset_t;

        vec[_0] = vec[_0]*mat[0];
        vec[_1] = vec[_1]*mat[3];
    }
    ''', 'Controlled4x4Multiply')


Controlled_Product_ctargs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4Product(const complex<float> val, complex<float>* vec, int c_index, int t_index) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c = (long long)1 << c_index;
        const long long offset_t = (long long)1 << t_index;
        const long long mask_c = offset_c - 1;
        const long long mask_t = offset_t - 1;

        long long gw=0, _0=0;

        if (t_index > c_index){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c)) + (label & mask_c);
        }
        else
        {
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t)) + (label & mask_t);
        }

        _0 = _0 + offset_t;
        vec[_0] = vec[_0]*val;
    }
    ''', 'Controlled4x4Product')


Controlled_Product_ctargs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4Product(const complex<double> val, complex<double>* vec, int c_index, int t_index){
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c = (long long)1 << c_index;
        const long long offset_t = (long long)1 << t_index;
        const long long mask_c = offset_c - 1;
        const long long mask_t = offset_t - 1;

        long long gw=0, _0=0;

        if (t_index > c_index){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c)) + (label & mask_c);
        }
        else
        {
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t)) + (label & mask_t);
        }

        _0 = _0 + offset_t;
        vec[_0] = vec[_0]*val;
    }
    ''', 'Controlled4x4Product')


Controlled_Product_cctarg_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled8x8Product(const complex<float> val, complex<float>* vec, int high, int low, int t_index) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c1 = (long long)1 << low;
        const long long offset_c2 = (long long)1 << high;
        const long long offset_t = (long long)1 << t_index;
        const long long maskc1 = offset_c1 - 1;
        const long long maskc2 = offset_c2 - 1;
        const long long mask_t = offset_t - 1;

        long long gw = 0, _0 = 0;

        if (t_index < low){
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c1 + (gw >> low << (low + 1)) + (gw & (offset_c1 - offset_t)) + (label & mask_t);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & maskc2);
        }else if(t_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c1)) + (label & maskc1);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & maskc2);
        }else{
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> high << (high + 1)) + (gw & (offset_c2 - offset_c1)) + (label & maskc1);
            _0 = offset_c2 + (_0 >> t_index << (t_index + 1)) + (_0 & mask_t);
        }

        _0 = _0 + offset_t;
        vec[_0] = vec[_0]*val;
    }
    ''', 'Controlled8x8Product')


Controlled_Product_cctarg_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled8x8Product(const complex<double> val, complex<double>* vec, int high, int low, int t_index){
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c1 = (long long)1 << low;
        const long long offset_c2 = (long long)1 << high;
        const long long offset_t = (long long)1 << t_index;
        const long long maskc1 = offset_c1 - 1;
        const long long maskc2 = offset_c2 - 1;
        const long long mask_t = offset_t - 1;

        long long gw = 0, _0 = 0;

        if (t_index < low){
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c1 + (gw >> low << (low + 1)) + (gw & (offset_c1 - offset_t)) + (label & mask_t);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & maskc2);
        }else if(t_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c1)) + (label & maskc1);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & maskc2);
        }else{
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> high << (high + 1)) + (gw & (offset_c2 - offset_c1)) + (label & maskc1);
            _0 = offset_c2 + (_0 >> t_index << (t_index + 1)) + (_0 & mask_t);
        }

        _0 = _0 + offset_t;
        vec[_0] = vec[_0]*val;
    }
    ''', 'Controlled8x8Product')


Controlled_InnerProduct_ctargs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4InnerProduct(const complex<float>* mat, complex<float>* vec, int c_index, int t_index) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c = (long long)1 << c_index;
        const long long offset_t = (long long)1 << t_index;
        const long long mask_c = offset_c - 1;
        const long long mask_t = offset_t - 1;

        long long gw=0, _0=0;

        if (t_index > c_index){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c)) + (label & mask_c);
        }
        else
        {
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t)) + (label & mask_t);
        }

        long long _1 = _0 + offset_t;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2] + vec[_1]*mat[3];
    }
    ''', 'Controlled4x4InnerProduct')


Controlled_InnerProduct_ctargs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4InnerProduct(const complex<double>* mat, complex<double>* vec, int c_index, int t_index) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c = (long long)1 << c_index;
        const long long offset_t = (long long)1 << t_index;
        const long long mask_c = offset_c - 1;
        const long long mask_t = offset_t - 1;

        long long gw=0, _0=0;

        if (t_index > c_index){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c)) + (label & mask_c);
        }
        else
        {
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t)) + (label & mask_t);
        }

        long long _1 = _0 + offset_t;

        complex<double> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2] + vec[_1]*mat[3];
    }
    ''', 'Controlled4x4InnerProduct')


Controlled_MultiplySwap_ctargs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4MultiSwap(const complex<float>* mat, complex<float>* vec, int c_index, int t_index) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c = (long long)1 << c_index;
        const long long offset_t = (long long)1 << t_index;
        const long long mask_c = offset_c - 1;
        const long long mask_t = offset_t - 1;

        long long gw=0, _0=0;

        if (t_index > c_index){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c)) + (label & mask_c);
        }
        else
        {
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t)) + (label & mask_t);
        }

        long long _1 = _0 + offset_t;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2];
    }
    ''', 'Controlled4x4MultiSwap')


Controlled_MultiplySwap_ctargs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4MultiSwap(const complex<double>* mat, complex<double>* vec, int c_index, int t_index) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c = (long long)1 << c_index;
        const long long offset_t = (long long)1 << t_index;
        const long long mask_c = offset_c - 1;
        const long long mask_t = offset_t - 1;

        long long gw=0, _0=0;

        if (t_index > c_index){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c)) + (label & mask_c);
        }
        else
        {
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t)) + (label & mask_t);
        }

        long long _1 = _0 + offset_t;

        complex<double> temp_0 = vec[_0];
        vec[_0] = vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2];
    }
    ''', 'Controlled4x4MultiSwap')


Controlled_Swap_targs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4Swap(int high, int low, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;

        complex<float> temp_0 = vec[_1];
        vec[_1] = vec[_2]*mat[6];
        vec[_2] = temp_0*mat[9];
    }
    ''', 'Controlled4x4Swap')


Controlled_Swap_targs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled4x4Swap(int high, int low, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;

        complex<double> temp_0 = vec[_1];
        vec[_1] = vec[_2]*mat[6];
        vec[_2] = temp_0*mat[9];
    }
    ''', 'Controlled4x4Swap')


Completed_MxIP_targs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void CompletedMxIP(int high, int low, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _2 + offset1;

        vec[_0] = vec[_0]*mat[0];
        vec[_3] = vec[_3]*mat[15];

        complex<float> temp_0 = vec[_1];
        vec[_1] = vec[_1]*mat[5] + vec[_2]*mat[6];
        vec[_2] = temp_0*mat[9] + vec[_2]*mat[10];
    }
    ''', 'CompletedMxIP')


Completed_MxIP_targs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void CompletedMxIP(int high, int low, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _2 + offset1;

        vec[_0] = vec[_0]*mat[0];
        vec[_3] = vec[_3]*mat[15];

        complex<double> temp_0 = vec[_1];
        vec[_1] = vec[_1]*mat[5] + vec[_2]*mat[6];
        vec[_2] = temp_0*mat[9] + vec[_2]*mat[10];
    }
    ''', 'CompletedMxIP')


Completed_IPxIP_targs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void CompletedIPxIP(int high, int low, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _2 + offset1;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_3]*mat[3];
        vec[_3] = temp_0*mat[12] + vec[_3]*mat[15];

        complex<float> temp_1 = vec[_1];
        vec[_1] = vec[_1]*mat[5] + vec[_2]*mat[6];
        vec[_2] = temp_1*mat[9] + vec[_2]*mat[10];
    }
    ''', 'CompletedIPxIP')


Completed_IPxIP_targs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void CompletedIPxIP(int high, int low, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << low;
        const long long offset2 = (long long)1 << high;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw = label >> low << (low + 1);
        long long _0 = (gw >> high << (high + 1)) + (gw & (offset2 - offset1)) + (label & mask1);

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _2 + offset1;

        complex<double> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_3]*mat[3];
        vec[_3] = temp_0*mat[12] + vec[_3]*mat[15];

        complex<double> temp_1 = vec[_1];
        vec[_1] = vec[_1]*mat[5] + vec[_2]*mat[6];
        vec[_2] = temp_1*mat[9] + vec[_2]*mat[10];
    }
    ''', 'CompletedIPxIP')


Diagonal_Multiply_normal_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void DiagxNormal(int t0, int t1, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset1 = (long long)1 << t0;
        const long long offset2 = (long long)1 << t1;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw=0, _0=0;

        if (t0 > t1){
            gw = label >> t1 << (t1 + 1);
            _0 = (gw >> t0 << (t0 + 1)) + (gw & (offset1 - offset2)) + (label & mask2);
        }
        else{
            gw = label >> t0 << (t0 + 1);
            _0 = (gw >> t1 << (t1 + 1)) + (gw & (offset2 - offset1)) + (label & mask1);
        }
        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _1 + offset2;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1];
        vec[_1] = temp_0*mat[4] + vec[_1]*mat[5];
        complex<float> temp_2 = vec[_2];
        vec[_2] = vec[_2]*mat[10] + vec[_3]*mat[11];
        vec[_3] =temp_2*mat[14] + vec[_3]*mat[15];
    }
    ''', 'DiagxNormal')


Diagonal_Multiply_normal_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void DiagxNormal(int t0, int t1, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        const long long offset1 = (long long)1 << t0;
        const long long offset2 = (long long)1 << t1;
        const long long mask1 = offset1 - 1;
        const long long mask2 = offset2 - 1;

        long long gw=0, _0=0;

        if (t0 > t1){
            gw = label >> t1 << (t1 + 1);
            _0 = (gw >> t0 << (t0 + 1)) + (gw & (offset1 - offset2)) + (label & mask2);
        }
        else{
            gw = label >> t0 << (t0 + 1);
            _0 = (gw >> t1 << (t1 + 1)) + (gw & (offset2 - offset1)) + (label & mask1);
        }

        long long _1 = _0 + offset1;
        long long _2 = _0 + offset2;
        long long _3 = _1 + offset2;

        complex<double> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1];
        vec[_1] = temp_0*mat[4] + vec[_1]*mat[5];

        complex<double> temp_2 = vec[_2];
        vec[_2] = vec[_2]*mat[10] + vec[_3]*mat[11];
        vec[_3] =temp_2*mat[14] + vec[_3]*mat[15];
    }
    ''', 'DiagxNormal')


RDiagonal_Swap_targ_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void RDiag2x2Swap(int parg, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _0 = (label >> parg << (parg + 1)) + (label & (offset - 1));
        long long _1 = _0 +  offset;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_1];
        vec[_1] = temp_0;
    }
    ''', 'RDiag2x2Swap')


RDiagonal_Swap_targ_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void RDiag2x2Swap(int parg, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _0 = (label >> parg << (parg + 1)) + (label & (offset - 1));
        long long _1 = _0 +  offset;

        complex<double> temp_0 = vec[_0];
        vec[_0] = vec[_1];
        vec[_1] = temp_0;
    }
    ''', 'RDiag2x2Swap')


RDiagonal_MultiplySwap_targ_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void RDiag2x2MultiSwap(int parg, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _0 = (label >> parg << (parg + 1)) + (label & (offset - 1));
        long long _1 = _0 +  offset;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2];
    }
    ''', 'RDiag2x2MultiSwap')


RDiagonal_MultiplySwap_targ_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void RDiag2x2MultiSwap(int parg, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        long long offset = (long long)1 << parg;

        long long _0 = (label >> parg << (parg + 1)) + (label & (offset - 1));
        long long _1 = _0 +  offset;

        complex<double> temp_0 = vec[_0];
        vec[_0] = vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2];
    }
    ''', 'RDiag2x2MultiSwap')


Controlled_Swap_more_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled8x8Swap(int high, int low, int t_index, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c1 = (long long)1 << low;
        const long long offset_c2 = (long long)1 << high;
        const long long offset_t = (long long)1 << t_index;
        const long long maskc1 = offset_c1 - 1;
        const long long maskc2 = offset_c2 - 1;
        const long long mask_t = offset_t - 1;

        long long gw = 0, _0 = 0;

        if (t_index < low){
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c1 + (gw >> low << (low + 1)) + (gw & (offset_c1 - offset_t)) + (label & mask_t);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & maskc2);
        }else if(t_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c1)) + (label & maskc1);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & maskc2);
        }else{
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> high << (high + 1)) + (gw & (offset_c2 - offset_c1)) + (label & maskc1);
            _0 = offset_c2 + (_0 >> t_index << (t_index + 1)) + (_0 & mask_t);
        }

        long long _1 = _0 + offset_t;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_1];
        vec[_1] = temp_0;
    }
    ''', 'Controlled8x8Swap')


Controlled_Swap_more_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled8x8Swap(int high, int low, int t_index, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c1 = (long long)1 << low;
        const long long offset_c2 = (long long)1 << high;
        const long long offset_t = (long long)1 << t_index;
        const long long maskc1 = offset_c1 - 1;
        const long long maskc2 = offset_c2 - 1;
        const long long mask_t = offset_t - 1;

        long long gw = 0, _0 = 0;

        if (t_index < low){
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c1 + (gw >> low << (low + 1)) + (gw & (offset_c1 - offset_t)) + (label & mask_t);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & maskc2);
        }else if(t_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c1)) + (label & maskc1);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & maskc2);
        }else{
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> high << (high + 1)) + (gw & (offset_c2 - offset_c1)) + (label & maskc1);
            _0 = offset_c2 + (_0 >> t_index << (t_index + 1)) + (_0 & mask_t);
        }

        long long _1 = _0 + offset_t;

        complex<double> temp_0 = vec[_0];
        vec[_0] = vec[_1];
        vec[_1] = temp_0;
    }
    ''', 'Controlled8x8Swap')


Controlled_Multiply_more_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled8x8Multiply(int high, int low, int t_index, const complex<float>* mat, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c1 = (long long)1 << low;
        const long long offset_c2 = (long long)1 << high;
        const long long offset_t = (long long)1 << t_index;
        const long long mask1 = offset_c1 - 1;
        const long long mask2 = offset_c2 - 1;
        const long long mask_t = offset_t - 1;

        long long gw = 0, _0 = 0;

        if (t_index < low){
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c1 + (gw >> low << (low + 1)) + (gw & (offset_c1 - offset_t)) + (label & mask_t);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & mask2);
        }else if(t_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c1)) + (label & mask1);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & mask2);
        }else{
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> high << (high + 1)) + (gw & (offset_c2 - offset_c1)) + (label & mask1);
            _0 = offset_c2 + (_0 >> t_index << (t_index + 1)) + (_0 & mask_t);
        }

        long long _1 = _0 + offset_t;

        vec[_0] = vec[_0]*mat[0];
        vec[_1] = vec[_1]*mat[3];
    }
    ''', 'Controlled8x8Multiply')


Controlled_Multiply_more_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled8x8Multiply(int high, int low, int t_index, const complex<double>* mat, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_c1 = (long long)1 << low;
        const long long offset_c2 = (long long)1 << high;
        const long long offset_t = (long long)1 << t_index;
        const long long mask1 = offset_c1 - 1;
        const long long mask2 = offset_c2 - 1;
        const long long mask_t = offset_t - 1;

        long long gw = 0, _0 = 0;

        if (t_index < low){
            gw = label >> t_index << (t_index + 1);
            _0 = offset_c1 + (gw >> low << (low + 1)) + (gw & (offset_c1 - offset_t)) + (label & mask_t);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & mask2);
        }else if(t_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> t_index << (t_index + 1)) + (gw & (offset_t - offset_c1)) + (label & mask1);
            _0 = offset_c2 + (_0 >> high << (high + 1)) + (_0 & mask2);
        }else{
            gw = label >> low << (low + 1);
            _0 = offset_c1 + (gw >> high << (high + 1)) + (gw & (offset_c2 - offset_c1)) + (label & mask1);
            _0 = offset_c2 + (_0 >> t_index << (t_index + 1)) + (_0 & mask_t);
        }

        long long _1 = _0 + offset_t;

        vec[_0] = vec[_0]*mat[0];
        vec[_1] = vec[_1]*mat[3];
    }
    ''', 'Controlled8x8Multiply')


Controlled_Swap_tmore_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled8x8Swapt(int high, int low, int c_index, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_t1 = (long long)1 << low;
        const long long offset_t2 = (long long)1 << high;
        const long long offset_c = (long long)1 << c_index;
        const long long mask1 = offset_t1 - 1;
        const long long mask2 = offset_t2 - 1;
        const long long mask_c = offset_c - 1;

        long long gw = 0, _0 = 0;

        if (c_index < low){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> low << (low + 1)) + (gw & (offset_t1 - offset_c)) + (label & mask_c);
            _0 = (_0 >> high << (high + 1)) + (_0 & mask2);
        }else if(c_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t1)) + (label & mask1);
            _0 = (_0 >> high << (high + 1)) + (_0 & mask2);
        }else{
            gw = label >> low << (low + 1);
            _0 = (gw >> high << (high + 1)) + (gw & (offset_t2 - offset_t1)) + (label & mask1);
            _0 = offset_c + (_0 >> c_index << (c_index + 1)) + (_0 & mask_c);
        }

        long long _1 = _0 + offset_t1;
        long long _2 = _0 + offset_t2;

        complex<float> temp_0 = vec[_1];
        vec[_1] = vec[_2];
        vec[_2] = temp_0;
    }
    ''', 'Controlled8x8Swapt')


Controlled_Swap_tmore_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void Controlled8x8Swapt(int high, int low, int c_index, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_t1 = (long long)1 << low;
        const long long offset_t2 = (long long)1 << high;
        const long long offset_c = (long long)1 << c_index;
        const long long mask1 = offset_t1 - 1;
        const long long mask2 = offset_t2 - 1;
        const long long mask_c = offset_c - 1;

        long long gw = 0, _0 = 0;

        if (c_index < low){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> low << (low + 1)) + (gw & (offset_t1 - offset_c)) + (label & mask_c);
            _0 = (_0 >> high << (high + 1)) + (_0 & mask2);
        }else if(c_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t1)) + (label & mask1);
            _0 = (_0 >> high << (high + 1)) + (_0 & mask2);
        }else{
            gw = label >> low << (low + 1);
            _0 = (gw >> high << (high + 1)) + (gw & (offset_t2 - offset_t1)) + (label & mask1);
            _0 = offset_c + (_0 >> c_index << (c_index + 1)) + (_0 & mask_c);
        }

        long long _1 = _0 + offset_t1;
        long long _2 = _0 + offset_t2;

        complex<double> temp_0 = vec[_1];
        vec[_1] = vec[_2];
        vec[_2] = temp_0;
    }
    ''', 'Controlled8x8Swapt')


def diagonal_targ(t_index, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between diagonal matrix (2x2) and state vector.

        $$ \begin{bmatrix}
        v_{00} & 0 \\
        0 & v_{11} \\
        \end{bmatrix}
        \cdot V
        $$

    """
    task_number = 1 << (vec_bit - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Diagonal_Multiply_targ_single_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, mat, vec)
        )
    else:
        Diagonal_Multiply_targ_double_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def diagonal_targs(t_indexes, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between diagonal matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        v_{00} & 0 & 0 & 0 \\
        0 & v_{11} & 0 & 0 \\
        0 & 0 & v_{22} & 0 \\
        0 & 0 & 0 & v_{33} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if t_indexes[0] > t_indexes[1]:
        high, low = t_indexes[0], t_indexes[1]
    else:
        high, low = t_indexes[1], t_indexes[0]

    if vec.dtype == np.complex64:
        Diagonal_Multiply_targs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )
    else:
        Diagonal_Multiply_targs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def normal_targ(t_index, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between normal matrix (2x2) and state vector.

        $$ \begin{bmatrix}
        v_{00} & v_{01} \\
        v_{10} & v_{11} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Based_InnerProduct_targ_single_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, mat, vec)
        )
    else:
        Based_InnerProduct_targ_double_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def normal_targs(t_indexes, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between normal matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        v_{00} & v_{01} & v_{02} & v_{03} \\
        v_{10} & v_{11} & v_{12} & v_{13} \\
        v_{20} & v_{21} & v_{22} & v_{23} \\
        v_{30} & v_{31} & v_{32} & v_{33} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Based_InnerProduct_targs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (t_indexes[0], t_indexes[1], mat, vec)
        )
    else:
        Based_InnerProduct_targs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (t_indexes[0], t_indexes[1], mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def control_targ(t_index, val, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between control matrix (2x2) and state vector.

        $$ \begin{bmatrix}
        1 & 0 \\
        0 & v_{11} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Controlled_Multiply_targ_single_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, val, vec)
        )
    else:
        Controlled_Multiply_targ_double_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, val, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def diagonal_ctargs(c_index, t_index, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between control diagonal matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & v_{22} & 0 \\
        0 & 0 & 0 & v_{33} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Controlled_Multiply_ctargs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (mat, vec, c_index, t_index)
        )
    else:
        Controlled_Multiply_ctargs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (mat, vec, c_index, t_index)
        )

    if sync:
        cp.cuda.Device().synchronize()


def control_ctargs(c_index, t_index, value, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between control matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & 1 & 0 \\
        0 & 0 & 0 & v_{33} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Controlled_Product_ctargs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (value, vec, c_index, t_index)
        )
    else:
        Controlled_Product_ctargs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (value, vec, c_index, t_index)
        )

    if sync:
        cp.cuda.Device().synchronize()


def control_cctarg(c_indexes, t_index, value, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between control matrix (8x8) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 0 & v_{77} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    if c_indexes[0] > c_indexes[1]:
        high, low = c_indexes[0], c_indexes[1]
    else:
        high, low = c_indexes[1], c_indexes[0]

    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Controlled_Product_cctarg_single_kernel(
            (block_num,),
            (thread_per_block,),
            (value, vec, high, low, t_index)
        )
    else:
        Controlled_Product_cctarg_double_kernel(
            (block_num,),
            (thread_per_block,),
            (value, vec, high, low, t_index)
        )

    if sync:
        cp.cuda.Device().synchronize()


def normal_ctargs(c_index, t_index, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between control normal matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & v_{22} & v_{23} \\
        0 & 0 & v_{32} & v_{33} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Controlled_InnerProduct_ctargs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (mat, vec, c_index, t_index)
        )
    else:
        Controlled_InnerProduct_ctargs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (mat, vec, c_index, t_index)
        )

    if sync:
        cp.cuda.Device().synchronize()


def ctrl_normal_targs(t_indexes, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between ctrl_normal matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & v_{00} & v_{01} & 0 \\
        0 & v_{10} & v_{11} & 0 \\
        0 & 0 & 0 & v_{33} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if t_indexes[0] > t_indexes[1]:
        high, low = t_indexes[0], t_indexes[1]
    else:
        high, low = t_indexes[1], t_indexes[0]

    if vec.dtype == np.complex64:
        Completed_MxIP_targs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )
    else:
        Completed_MxIP_targs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def normal_normal_targs(t_indexes, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between normal_normal matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        v_{00} & 0 & 0 & v_{03} \\
        0 & v_{11} & v_{12} & 0 \\
        0 & v_{21} & v_{22} & 0 \\
        v_{30} & 0 & 0 & v_{33} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if t_indexes[0] > t_indexes[1]:
        high, low = t_indexes[0], t_indexes[1]
    else:
        high, low = t_indexes[1], t_indexes[0]

    if vec.dtype == np.complex64:
        Completed_IPxIP_targs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )
    else:
        Completed_IPxIP_targs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def diagonal_normal_targs(t_indexes, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between diag_normal matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        v_{00} & v_{01} & 0 & 0 \\
        v_{10} & v_{11} & 0 & 0 \\
        0 & 0 & v_{22} & v_{23} \\
        0 & 0 & v_{32} & v_{33} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Diagonal_Multiply_normal_single_kernel(
            (block_num,),
            (thread_per_block,),
            (t_indexes[0], t_indexes[1], mat, vec)
        )
    else:
        Diagonal_Multiply_normal_double_kernel(
            (block_num,),
            (thread_per_block,),
            (t_indexes[0], t_indexes[1], mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def swap_targ(t_index, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between Swap's matrix (2x2) and state vector.

        $$ \begin{bmatrix}
        0 & 1 \\
        1 & 0 \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        RDiagonal_Swap_targ_single_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, vec)
        )
    else:
        RDiagonal_Swap_targ_double_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def reverse_targ(t_index, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between reverse matrix (2x2) and state vector.

        $$ \begin{bmatrix}
        0 & v_{01} \\
        v_{10} & 0 \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        RDiagonal_MultiplySwap_targ_single_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, mat, vec)
        )
    else:
        RDiagonal_MultiplySwap_targ_double_kernel(
            (block_num,),
            (thread_per_block,),
            (t_index, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def reverse_targs(t_indexes, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between reverse matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        0 & 0 & 0 & v_{03} \\
        0 & 0 & v_{12} & 0 \\
        0 & v_{21} & 0 & 0 \\
        v_{30} & 0 & 0 & 0 \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if t_indexes[0] > t_indexes[1]:
        high, low = t_indexes[0], t_indexes[1]
    else:
        high, low = t_indexes[1], t_indexes[0]

    if vec.dtype == np.complex64:
        RDiagonal_Multiply_targs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )
    else:
        RDiagonal_Multiply_targs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def reverse_ctargs(c_index, t_index, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between control reverse matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & 0 & v_{23} \\
        0 & 0 & v_{32} & 0 \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if vec.dtype == np.complex64:
        Controlled_MultiplySwap_ctargs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (mat, vec, c_index, t_index)
        )
    else:
        Controlled_MultiplySwap_ctargs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (mat, vec, c_index, t_index)
        )

    if sync:
        cp.cuda.Device().synchronize()


def swap_targs(t_indexes, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between swap matrix (4x4) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 \\
        0 & 0 & v_{12} & 0 \\
        0 & v_{21} & 0 & 0 \\
        0 & 0 & 0 & 1 \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 2)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if t_indexes[0] > t_indexes[1]:
        high, low = t_indexes[0], t_indexes[1]
    else:
        high, low = t_indexes[1], t_indexes[0]

    if vec.dtype == np.complex64:
        Controlled_Swap_targs_single_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )
    else:
        Controlled_Swap_targs_double_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def reverse_more(c_indexes, t_index, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between reverse matrix (8x8) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 3)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if c_indexes[0] > c_indexes[1]:
        high, low = c_indexes[0], c_indexes[1]
    else:
        high, low = c_indexes[1], c_indexes[0]

    if vec.dtype == np.complex64:
        Controlled_Swap_more_single_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, t_index, vec)
        )
    else:
        Controlled_Swap_more_double_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, t_index, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def diagonal_more(c_indexes, t_index, mat, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between control diagonal matrix (8x8) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & v_{66} & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 0 & v_{77} \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 3)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if c_indexes[0] > c_indexes[1]:
        high, low = c_indexes[0], c_indexes[1]
    else:
        high, low = c_indexes[1], c_indexes[0]

    if vec.dtype == np.complex64:
        Controlled_Multiply_more_single_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, t_index, mat, vec)
        )
    else:
        Controlled_Multiply_more_double_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, t_index, mat, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


def swap_tmore(t_indexes, c_index, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between control swap matrix (8x8) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 3)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if t_indexes[0] > t_indexes[1]:
        high, low = t_indexes[0], t_indexes[1]
    else:
        high, low = t_indexes[1], t_indexes[0]

    if vec.dtype == np.complex64:
        Controlled_Swap_tmore_single_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, c_index, vec)
        )
    else:
        Controlled_Swap_tmore_double_kernel(
            (block_num,),
            (thread_per_block,),
            (high, low, c_index, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


Apply_RCCX_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void RCCX8x8Gate(int c_index, int high, int low, int t0, int t1, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_t1 = (long long)1 << low;
        const long long offset_t2 = (long long)1 << high;
        const long long offset_c = (long long)1 << c_index;
        const long long mask1 = offset_t1 - 1;
        const long long mask2 = offset_t2 - 1;
        const long long mask_c = offset_c - 1;

        long long gw = 0, _0 = 0;

        if (c_index < low){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> low << (low + 1)) + (gw & (offset_t1 - offset_c)) + (label & mask_c);
            _0 = (_0 >> high << (high + 1)) + (_0 & mask2);
        }else if(c_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t1)) + (label & mask1);
            _0 = (_0 >> high << (high + 1)) + (_0 & mask2);
        }else{
            gw = label >> low << (low + 1);
            _0 = (gw >> high << (high + 1)) + (gw & (offset_t2 - offset_t1)) + (label & mask1);
            _0 = offset_c + (_0 >> c_index << (c_index + 1)) + (_0 & mask_c);
        }

        long long _x0 = _0 + (1 << t1);
        long long _x1 = _x0 + (1 << t0);
        long long _neg = _0 + (1 << t0);

        complex<float> temp_0 = vec[_x0];
        complex<float> neg = -1;
        vec[_x0] = vec[_x1];
        vec[_x1] = temp_0;
        vec[_neg] = neg * vec[_neg];
    }
    ''', 'RCCX8x8Gate')


Apply_RCCX_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void RCCX8x8Gate(int c_index, int high, int low, int t0, int t1, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;

        const long long offset_t1 = (long long)1 << low;
        const long long offset_t2 = (long long)1 << high;
        const long long offset_c = (long long)1 << c_index;
        const long long mask1 = offset_t1 - 1;
        const long long mask2 = offset_t2 - 1;
        const long long mask_c = offset_c - 1;

        long long gw = 0, _0 = 0;

        if (c_index < low){
            gw = label >> c_index << (c_index + 1);
            _0 = offset_c + (gw >> low << (low + 1)) + (gw & (offset_t1 - offset_c)) + (label & mask_c);
            _0 = (_0 >> high << (high + 1)) + (_0 & mask2);
        }else if(c_index < high){
            gw = label >> low << (low + 1);
            _0 = offset_c + (gw >> c_index << (c_index + 1)) + (gw & (offset_c - offset_t1)) + (label & mask1);
            _0 = (_0 >> high << (high + 1)) + (_0 & mask2);
        }else{
            gw = label >> low << (low + 1);
            _0 = (gw >> high << (high + 1)) + (gw & (offset_t2 - offset_t1)) + (label & mask1);
            _0 = offset_c + (_0 >> c_index << (c_index + 1)) + (_0 & mask_c);
        }

        long long _x0 = _0 + (1 << t1);
        long long _x1 = _x0 + (1 << t0);
        long long _neg = _0 + (1 << t0);

        complex<double> neg = -1;
        vec[_neg] = neg * vec[_neg];
        complex<double> temp_0 = vec[_x0];
        vec[_x0] = vec[_x1];
        vec[_x1] = temp_0;
    }
    ''', 'RCCX8x8Gate')


def apply_rccxgate(c_index, t_indexes, vec, vec_bit, sync: bool = False):
    r""" Apply dot operator between reverse matrix (8x8) and state vector.

        $$ \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & -1 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\
        \end{bmatrix}
        \cdot V
        $$
    """
    task_number = 1 << (vec_bit - 3)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    if t_indexes[0] > t_indexes[1]:
        high, low = t_indexes[0], t_indexes[1]
    else:
        high, low = t_indexes[1], t_indexes[0]

    if vec.dtype == np.complex64:
        Apply_RCCX_single_kernel(
            (block_num,),
            (thread_per_block,),
            (c_index, high, low, t_indexes[0], t_indexes[1], vec)
        )
    else:
        Apply_RCCX_double_kernel(
            (block_num,),
            (thread_per_block,),
            (c_index, high, low, t_indexes[0], t_indexes[1], vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


"""
Special Gates: MeasureGate, ResetGate and PermGate
"""
prop_add_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void ProbAddSingle(const int index, const int block, complex<float>* vec, complex<float>* out) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long based = label << block;
        long long _0 = (based & (((long long)1 << index) - 1))
                + (based >> index << (index + 1));
        out[label] = abs(vec[_0]) * abs(vec[_0]);
        for(int i = 1; i < (1 << block); i++){
            long long temp = based + i;
            temp = (temp & (((long long)1 << index) - 1))
                + (temp >> index << (index + 1));
            out[label] += abs(vec[temp]) * abs(vec[temp]);
        }
    }
    ''', 'ProbAddSingle')


prop_add_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void ProbAddDouble(const int index, const int block, complex<double>* vec, complex<double>* out) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long based = label << block;
        long long _0 = (based & (((long long)1 << index) - 1))
                + (based >> index << (index + 1));
        out[label] = abs(vec[_0]) * abs(vec[_0]);
        for(int i = 1; i < (1 << block); i++){
            long long temp = based + i;
            temp = (temp & (((long long)1 << index) - 1))
                + (temp >> index << (index + 1));
            out[label] += abs(vec[temp]) * abs(vec[temp]);
        }
    }
    ''', 'ProbAddDouble')


MeasureGate_prop = cp.ReductionKernel(
    'T x',
    'T y',
    'x',
    'a + b',
    'y = abs(a)',
    '0',
    'MeasureGate_prop'
)


mn_measureprob_calculator = cp.ReductionKernel(
    'T x',
    'T y',
    'x',
    'a + b',
    'y = abs(a)*abs(a)',
    '0',
    'mn_measureprob_calculator'
)


MeasureGate0_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void MeasureGate0Single(const int index, const float generation, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long _0 = (label & (((long long)1 << index) - 1))
                + (label >> index << (index + 1));
        long long _1 = _0 + ((long long)1 << index);
        vec[_0] = vec[_0] * generation;
        vec[_1] = complex<float>(0, 0);
    }
    ''', 'MeasureGate0Single')


MeasureGate1_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void MeasureGate1Single(const int index, const float generation, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long _0 = (label & (((long long)1 << index) - 1))
                + (label >> index << (index + 1));
        long long _1 = _0 + ((long long)1 << index);
        vec[_0] = complex<float>(0, 0);
        vec[_1] = vec[_1] * generation;
    }
    ''', 'MeasureGate1Single')


MeasureGate0_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void MeasureGate0Double(const int index, const double generation, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long _0 = (label & (((long long)1 << index) - 1))
                + (label >> index << (index + 1));
        long long _1 = _0 + ((long long)1 << index);
        vec[_0] = vec[_0] * generation;
        vec[_1] = complex<double>(0, 0);
    }
    ''', 'MeasureGate0Double')


MeasureGate1_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void MeasureGate1Double(const int index, const double generation, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long _0 = (label & (((long long)1 << index) - 1))
                + (label >> index << (index + 1));
        long long _1 = _0 + ((long long)1 << index);
        vec[_0] = complex<double>(0, 0);
        vec[_1] = vec[_1] * generation;
    }
    ''', 'MeasureGate1Double')


ResetGate0_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void ResetGate0Float(const int index, const float generation, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long _0 = (label & (((long long)1 << index) - 1))
                + (label >> index << (index + 1));
        long long _1 = _0 + ((long long)1 << index);
        vec[_0] = vec[_0] / generation;
        vec[_1] = complex<float>(0, 0);
    }
    ''', 'ResetGate0Float')


ResetGate1_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void ResetGate1Float(const int index, const float generation, complex<float>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long _0 = (label & (((long long)1 << index) - 1))
                + (label >> index << (index + 1));
        long long _1 = _0 + ((long long)1 << index);

        vec[_0] = vec[_1];
        vec[_1] = complex<float>(0, 0);
    }
    ''', 'ResetGate1Float')


ResetGate0_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void ResetGate0Double(const int index, const double generation, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long _0 = (label & (((long long)1 << index) - 1))
                + (label >> index << (index + 1));
        long long _1 = _0 + ((long long)1 << index);
        vec[_0] = vec[_0] / generation;
        vec[_1] = complex<double>(0, 0);
    }
    ''', 'ResetGate0Double')


ResetGate1_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void ResetGate1Double(const int index, const double generation, complex<double>* vec) {
        long long label = blockDim.x * blockIdx.x + threadIdx.x;
        long long _0 = (label & (((long long)1 << index) - 1))
                + (label >> index << (index + 1));
        long long _1 = _0 + ((long long)1 << index);

        vec[label] = vec[_1];
    }
    ''', 'ResetGate1Double')


def measured_prob_calculate(index, vec, vec_bit, all_measured: bool = False, sync: bool = False):
    """ Calculate the probability to measured 0. """
    # Deal with the whole vector state measured, only happen for multi-nodes simulator
    if all_measured:
        prob = mn_measureprob_calculator(vec)
        return prob.real

    # Kernel function preparation
    pre_added_qubits = MEASURED_PRE_ADDED if vec_bit > MEASURED_PRE_ADDED + 20 else 0
    task_number = 1 << (vec_bit - (pre_added_qubits + 1))

    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block
    out = cp.empty(task_number, dtype=vec.dtype)

    # Calculated the probability of measured 1 at current index
    kernel_functions = prop_add_double_kernel if vec.dtype == np.complex128 else prop_add_single_kernel
    kernel_functions(
        (block_num, ),
        (thread_per_block, ),
        (index, pre_added_qubits, vec, out)
    )

    prob = MeasureGate_prop(out, axis=0).real

    if sync:
        cp.cuda.Device().synchronize()

    return prob


def apply_measuregate(index, vec, vec_bit, prob, sync: bool = False):
    """
    Measure Gate Measure.
    """
    # Kernel function preparation
    task_number = 1 << (vec_bit - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block
    if vec.dtype == np.complex64:
        kernel_functions = (MeasureGate0_single_kernel, MeasureGate1_single_kernel)
        float_type = np.float32
    else:
        kernel_functions = (MeasureGate0_double_kernel, MeasureGate1_double_kernel)
        float_type = np.float64

    # Apply to state vector
    _0 = random.random()
    _1 = _0 > prob
    if not _1:
        alpha = float_type(1 / np.sqrt(prob))
        kernel_functions[0](
            (block_num, ),
            (thread_per_block, ),
            (index, alpha, vec)
        )
    else:
        alpha = float_type(1 / np.sqrt(1 - prob))
        kernel_functions[1](
            (block_num,),
            (thread_per_block,),
            (index, alpha, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()

    return _1


def apply_resetgate(index, vec, vec_bit, prob, sync: bool = False):
    """
    Measure Gate Measure.
    """
    # Kernel function preparation
    task_number = 1 << (vec_bit - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block
    if vec.dtype == np.complex64:
        kernel_functions = (ResetGate0_single_kernel, ResetGate1_single_kernel)
    else:
        kernel_functions = (ResetGate0_double_kernel, ResetGate1_double_kernel)

    # Apply to state vector
    alpha = np.float64(np.sqrt(prob))
    if alpha < 1e-6:
        kernel_functions[1](
            (block_num, ),
            (thread_per_block,),
            (index, alpha, vec)
        )
    else:
        kernel_functions[0](
            (block_num,),
            (thread_per_block,),
            (index, alpha, vec)
        )

    if sync:
        cp.cuda.Device().synchronize()


multi_control_targ_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void MultiControlTarg(
        const complex<float>* mat,
        complex<float>* vec,
        int fixed, int t_index, int mat_bit, int* mat_args
    ) {
        int label = blockDim.x * blockIdx.x + threadIdx.x;
        const int offset_t = 1 << t_index;

        int other = label & ((1 << mat_args[0]) - 1);
        int gw = label >> mat_args[0] << (mat_args[0] + 1);
        for(int i = 1; i < mat_bit; i++){
            other += gw & ((1 << mat_args[i]) - (1 << mat_args[i - 1]));
            gw = gw >> mat_args[i] << (mat_args[i] + 1);
        }
        other += gw;

        int _0 = other + fixed;
        int _1 = _0 + offset_t;

        complex<float> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2] + vec[_1]*mat[3];
    }
    ''', 'MultiControlTarg')


multi_control_targ_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void MultiControlTarg(
        const complex<double>* mat,
        complex<double>* vec,
        int fixed, int t_index, int mat_bit, int* mat_args
    ) {
        int label = blockDim.x * blockIdx.x + threadIdx.x;
        const int offset_t = 1 << t_index;

        int other = label & ((1 << mat_args[0]) - 1);
        int gw = label >> mat_args[0] << (mat_args[0] + 1);
        for(int i = 1; i < mat_bit; i++){
            other += gw & ((1 << mat_args[i]) - (1 << mat_args[i - 1]));
            gw = gw >> mat_args[i] << (mat_args[i] + 1);
        }
        other += gw;

        int _0 = other + fixed;
        int _1 = _0 + offset_t;

        complex<double> temp_0 = vec[_0];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1];
        vec[_1] = temp_0*mat[2] + vec[_1]*mat[3];
    }
    ''', 'MultiControlTarg')


def apply_multi_control_targ_gate(
    vec: cp.array,
    qubits: int,
    mat: cp.array,
    c_indexes: list,
    t_index: int,
    sync: bool = False
):
    """ Apply dot operator for multi-control gate's matrix and state vector.
    only working for the gate with 1 target qubit.
    """
    # Get Fixed indexes by given c_indexes
    based_idx = 0
    for cidx in c_indexes:
        based_idx += 1 << cidx

    mat_args = c_indexes.copy()
    mat_args.append(t_index)
    mat_args.sort()
    mat_args = cp.array(mat_args, dtype=np.int32)
    mat_bit = len(mat_args)

    # GPU preparation
    task_number = 1 << (qubits - len(c_indexes) - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    # Start GPU kernel function
    kernel_function = multi_control_targ_single_kernel if vec.dtype == np.complex64 else \
        multi_control_targ_double_kernel
    kernel_function(
        (block_num,),
        (thread_per_block,),
        (mat, vec, based_idx, t_index, mat_bit, mat_args)
    )

    if sync:
        cp.cuda.Device().synchronize()


multi_control_targs_single_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void MultiControlTarg(
        const complex<float>* mat,
        complex<float>* vec,
        int fixed, int* t_indexes, int mat_bit, int* mat_args
    ) {
        int label = blockDim.x * blockIdx.x + threadIdx.x;
        const int offset_t1 = 1 << t_indexes[0];
        const int offset_t2 = 1 << t_indexes[1];

        int other = label & ((1 << mat_args[0]) - 1);
        int gw = label >> mat_args[0] << (mat_args[0] + 1);
        for(int i = 1; i < mat_bit; i++){
            other += gw & ((1 << mat_args[i]) - (1 << mat_args[i - 1]));
            gw = gw >> mat_args[i] << (mat_args[i] + 1);
        }
        other += gw;

        int _0 = other + fixed;
        int _1 = _0 + offset_t1;
        int _2 = _0 + offset_t2;
        int _3 = _1 + offset_t2;

        complex<float> temp_0 = vec[_0], temp_1 = vec[_1], temp_2 = vec[_2];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1] + vec[_2]*mat[2] + vec[_3]*mat[3];
        vec[_1] = temp_0*mat[4] + vec[_1]*mat[5] + vec[_2]*mat[6] + vec[_3]*mat[7];
        vec[_2] = temp_0*mat[8] + temp_1*mat[9] + vec[_2]*mat[10] + vec[_3]*mat[11];
        vec[_3] = temp_0*mat[12] + temp_1*mat[13] + temp_2*mat[14] + vec[_3]*mat[15];
    }
    ''', 'MultiControlTarg')


multi_control_targs_double_kernel = cp.RawKernel(r'''
    #include <cupy/complex.cuh>
    extern "C" __global__
    void MultiControlTarg(
        const complex<double>* mat,
        complex<double>* vec,
        int fixed, int* t_indexes, int mat_bit, int* mat_args
    ) {
        int label = blockDim.x * blockIdx.x + threadIdx.x;
        const int offset_t1 = 1 << t_indexes[0];
        const int offset_t2 = 1 << t_indexes[1];

        int other = label & ((1 << mat_args[0]) - 1);
        int gw = label >> mat_args[0] << (mat_args[0] + 1);
        for(int i = 1; i < mat_bit; i++){
            other += gw & ((1 << mat_args[i]) - (1 << mat_args[i - 1]));
            gw = gw >> mat_args[i] << (mat_args[i] + 1);
        }
        other += gw;

        int _0 = other + fixed;
        int _1 = _0 + offset_t1;
        int _2 = _0 + offset_t2;
        int _3 = _1 + offset_t2;

        complex<double> temp_0 = vec[_0], temp_1 = vec[_1], temp_2 = vec[_2];
        vec[_0] = vec[_0]*mat[0] + vec[_1]*mat[1] + vec[_2]*mat[2] + vec[_3]*mat[3];
        vec[_1] = temp_0*mat[4] + vec[_1]*mat[5] + vec[_2]*mat[6] + vec[_3]*mat[7];
        vec[_2] = temp_0*mat[8] + temp_1*mat[9] + vec[_2]*mat[10] + vec[_3]*mat[11];
        vec[_3] = temp_0*mat[12] + temp_1*mat[13] + temp_2*mat[14] + vec[_3]*mat[15];
    }
    ''', 'MultiControlTarg')


def apply_multi_control_targs_gate(
    vec: cp.array,
    qubits: int,
    mat: cp.array,
    c_indexes: list,
    t_indexes: list,
    sync: bool = False
):
    """ Apply dot operator for multi-control gate's matrix and state vector.
    only working for the gate with 2 target qubit.
    """
    # Get Fixed indexes by given c_indexes
    based_idx = 0
    for cidx in c_indexes:
        based_idx += 1 << cidx

    mat_args = c_indexes.copy() + t_indexes.copy()
    mat_args.sort()
    mat_args = cp.array(mat_args, dtype=np.int32)
    t_args = cp.array(t_indexes, dtype=np.int32)
    mat_bit = len(mat_args)

    # GPU preparation
    task_number = 1 << (qubits - len(c_indexes) - 1)
    thread_per_block = min(DEFAULT_BLOCK_NUM, task_number)
    block_num = task_number // thread_per_block

    # Start GPU kernel function
    kernel_function = multi_control_targs_single_kernel if vec.dtype == np.complex64 else \
        multi_control_targs_double_kernel
    kernel_function(
        (block_num,),
        (thread_per_block,),
        (mat, vec, based_idx, t_args, mat_bit, mat_args)
    )

    if sync:
        cp.cuda.Device().synchronize()


kernel_funcs = list(locals().keys())
for name in kernel_funcs:
    if name.endswith("kernel"):
        locals()[name].compile()
