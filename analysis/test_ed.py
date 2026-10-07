import numpy as np, time
from ed import full_spectrum, brute_force_spectrum
for (L,S,th) in [(4,1,0),(5,1,0),(6,1,0),(6,1,np.pi),(6,1,2*np.pi/3),(5,1,np.pi),(4,1,np.pi),(6,0.5,0),(8,0.5,0),(8,0.5,np.pi),(7,0.5,0)]:
    E,W = full_spectrum(L,S,th,verbose=False)
    Ef = np.repeat(E,W)
    Eb = brute_force_spectrum(L,S,th)
    print(L,S,round(th,4),'maxdiff',np.abs(np.sort(Ef)-Eb).max(), 'E0',Eb[0], 'E1', Eb[np.argmax(Eb>Eb[0]+1e-9)])
# benchmark dense eigvalsh
import scipy.linalg as sla
for n in [3000,6000]:
    A = np.random.randn(n,n)+1j*np.random.randn(n,n); A=A+A.conj().T
    t=time.time(); sla.eigvalsh(A,overwrite_a=True,check_finite=False); print('complex',n,time.time()-t)
    A = np.random.randn(n,n); A=A+A.T
    t=time.time(); sla.eigvalsh(A,overwrite_a=True,check_finite=False); print('real',n,time.time()-t)
