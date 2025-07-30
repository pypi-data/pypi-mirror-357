#ifndef CONSBALLWALK_HPP
#define CONSBALLWALK_HPP

#include "SparseRandomWalk.hpp"

class SparseBallWalk : public SparseRandomWalk{
    public:
        /**
         * @brief initialization of Sparse Ball Walk class
         * @param r spread parameter
         * @param thin thin parameter
         */
        SparseBallWalk(double r, int thin = 1) : R(r), SparseRandomWalk(thin, 0.0){}

         /**
         * @brief generate values from the Ball walk (constrained)
         * @param num_steps number of steps wanted to take
         * @param init initial starting point
         * @param A polytope matrix 
         * @param b polytope vector
         * @param k k values >= 0 constraint
         * @param burn number of initial steps to cut
         * @param seed seed for reproducibility
         * @return num_steps by d (dimension of x) matrix
         */
        MatrixXd generateCompleteWalk(
            const int num_steps, 
            const VectorXd& init, 
            const SparseMatrixXd& A, 
            const VectorXd& b, 
            int k, 
            int burn,
            int seed
            ) override;
    
    protected:
        /**
         * @brief spread parameter
         */
        const double R;
};
#endif 