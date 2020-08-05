
import numpy as np

def GS(P):
    '''
    Input:
       P: n x d random matrix
     Output:
       P_ortho: each column orthogonal while maintaining length
     Performing modified Gram–Schmidt process
    '''
    
    d = P.shape[1]
    temp_l = np.linalg.norm(P, axis = 1)
    for i in range(d):
        temp_row = P[:,i]
        for j in range(i - 1):
            temp_j = P[:,j]
            temp_product = temp_row.T.dot(temp_j) / (temp_l[j] ** 2)
            temp_row -= temp_product * temp_j 
        temp_row *= temp_l[i] / np.sqrt(temp_row.T.dot(temp_row))
        P[:,i] = temp_row;
    return P


def Projection(A, q, d, Ortho, seed):
    '''
    Inputs:
        A: sparse adjacency matrix
        q: order
        d: dimensionality
        Ortho: whether use orthogonal projection
        seed: random seed
    Outputs:
        U_list: a list of R, A * R, A^2 * R ... A^q * R
    '''
    
    N = A.shape[0]
    np.random.seed(seed)                                   # set random seed
    U_list = [np.random.normal(0, 1.0/np.sqrt(d),(N,d))]   # Gaussian random matrix
    if Ortho:                                              # whether use orthogonal projection
        U_list[0] = GS(U_list[0])
    for i in range(q):                                     # iterative random projection
        U_list.append(A.dot(U_list[-1]))
    return U_list


def Combine(U_list, weights):
    '''
    Inputs:
       U_list: a list of decomposed parts, generated by RandNE_Projection
       weights: a vector of weights for each order, w_0 ... w_q
    Outputs:
       U: final embedding vector
    '''
    
    if not len(U_list) == len(weights):
        raise ValueError('Weight length not consistent')
    U = np.zeros(U_list[0].shape)
    for i in range(len(weights)):
        U += weights[i] * U_list[i]
    return U
    
def Update(A, delta_A, U_list, Ortho = False, seed = 0):
    '''
    Inputs:
        A: original adjacency matrix
        delta_A: the changes of adjacency matrix
        U_list: original decomposed parts
        Ortho: whether use orthogonal projection
        seed: random seed
    Outputs:
        U_list: updated decomposed parts
    '''
    
    q = len(U_list)                     # order + 1
    N, d = U_list[0].shape              # dimension
    N_new = delta_A.shape[0]        
    
    if N_new > N:                       # if new users, adjust dimensionality
        if not hasattr(A,'resize'):
            raise RuntimeError('Please update Scipy')
        A.resize((N_new,N_new))
        for i in range(1,len(U_list)):
            U_list[i] = np.insert(U_list[i], N, np.zeros((N_new - N, d)),0)
        np.random.seed(seed)                                
        U_list[0] = np.insert(U_list[0], N, np.random.normal(0, 1.0/np.sqrt(d),(N_new - N, d)), 0)
        if Ortho:                                      
            U_list[0] = GS(U_list[0])
        N = N_new;
    
    delta_U = [np.zeros((N,d))]         # calculate changed parts
    for i in range(1, q):
        delta_U.append(delta_A.dot(U_list[i-1]) + A.dot(delta_U[i-1]) + delta_A.dot(delta_U[i-1]))
        
    for i in range(1, q):
        U_list[i] += delta_U[i]
        
    return U_list