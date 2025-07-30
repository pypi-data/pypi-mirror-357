import mvulib
import matlab
import numpy as np
import time
from scipy.sparse import csr_matrix

class Mvu:
    # Statička instanca za pristup implementaciji u MATLAB-u.
    _library_instance=None
    
    def __init__(self, n_neighbors=5, angles=False, maxiter=150, verbose=True):

        # Broj susjeda koji koristimo u konstrukciji kNN grafa.
        self.n_neighbors=n_neighbors

        # Da li želimo sačuvati kuteve u susjedstvu točaka ili samo udaljenosti.
        self.angles=angles

        # Maksimalan broj iteracija SeDuMi solvera. Obično ne treba više od 50.
        self.maxiter=maxiter

        # Ispis prilikom izvršavanja.
        self.verbose=verbose

        # Broj uzoraka u skupu ulaznih podataka.
        self.n_samples=None

        # Broj značajki u skupu ulaznih podataka.
        self.n_features=None

        # Rijetka matrica susjedstva A povezanog neusmjerenog grafa
        # koji koristi MVU.
        self.adjacency_matrix=None

        # Simetrična pozitivno semidefinitna (PSD) matrica K određena
        # semidefinitnim programiranjem (SDP).
        self.kernel=None

        # MVU cijena jezgre K (njen trag).
        self.cost=None

        # Da li je jezgra K centrirana. Ne mora biti ako nam konvergencija
        # nije bila dovoljno dobra.
        self.centered=None

        # Svojstvene vrijednosti centrirane jezgre Kc=HKH silazno poredane.
        # Kc je efektivna jezgra koju koristimo kod kMDS-a da bi dobili
        # smještenje u odnosu na prostor značajki.
        self.eigenvalues=None

        # Matrica reda n kojom su dana smještenja kMDS-a za izbor jezgre Kc i
        # svaki p<=n. p-dimenzionalno smještenje kMDS-a dobivamo izborom prvih
        # p stupaca ove matrice.
        self._Y=None

        # Ciljna dimenzija p koju zadajemo pri pozivu funcije Mvu.transform().
        self.n_components=None

        # Smještenje Y kMDS-a za izbor jezgre Kc i ciljne dimenzije p.
        self.embedding=None

        # Greška rekonstrukcije kMDS-a za smještenje Y.
        self.reconstruction_error=None

        # Relativna greška rekonstrukcije za Y.
        self.reconstruction_error_rel=None

        # Broj ograničenja optimizacije.
        self.n_constraints=None

        # Zadnja dostignuta iteracija.
        self.iter=None

        # Indikator dopustivosti rješenja obično između -1 i 1.
        # Trebao bi biti blizu 1 za dopustiva rješenja (SeDuMi).
        self.feasratio=None

        # Status u kojem je rješavanje završilo. Vrijednosti 0 ili 1
        # označavaju da je konvergencija (dovoljno) dobra, dok 2 označava
        # neuspješnu konvergenciju (SeDuMi).
        self.numerr=None
    

    # Inicijalizacija instance bibilioteke.
    def initialize():
        if not Mvu._library_instance:
            Mvu._library_instance=mvulib.initialize()

    # Uništavanje instance bibilioteke.
    def terminate():
        if Mvu._library_instance:
            Mvu._library_instance.terminate()
            Mvu._library_instance=None
            
    def __str__(self):
        return f"n_neighbors={self.n_neighbors}, angles={self.angles},"+\
               f" maxiter={self.maxiter}"

    def fit(self, X):
        if self.verbose:
            print("============================== Mvu ==============================")
            
        start=time.time()

        # Ako je statička instanca biblioteke definirana koristimo nju, dok u
        # protivnom stvaramo instancu samo za potrebe ove metode.
        lib=None
        if Mvu._library_instance:
            lib=Mvu._library_instance
        else:
            lib=mvulib.initialize()

        n, d=X.shape
        self.n_samples=n
        self.n_features=d

        if self.verbose:
            print(f"Parameters:\nn_samples={n}\nn_features={d}"+\
                  f"\nn_neighbors={self.n_neighbors}"+\
                  f"\nangles={self.angles}\nmaxiter={self.maxiter}")

        # Definicija parametara koja prosljeđujemo MATLAB funkciji.
        XIn=matlab.double(X, size=(n,d))
        kIn=matlab.double([self.n_neighbors], size=(1,1))
        anglesStrIn="angles"
        anglesIn=matlab.double([1.0 if self.angles else 0.0], size=(1,1))
        maxIterStrIn="maxiter"
        maxIterIn=matlab.double([self.maxiter], size=(1,1))

        if self.verbose:
            print("Solving problem...")

        YOut, infoOut=lib.mvu(XIn, kIn, anglesStrIn, anglesIn, \
                              maxIterStrIn, maxIterIn,  nargout=2)
        if self.verbose:
            print("Problem solved!")

        self._Y=np.array(YOut)
        self.cost=infoOut["cost"]
        self.centered=True if infoOut["cent"] else False
        self.eigenvalues=np.array(infoOut["eigvals"])
        self.n_constraints=int(infoOut["constr"])
        self.iter=int(infoOut["iter"])
        self.feasratio=infoOut["feasratio"]
        self.numerr=int(infoOut["numerr"])
        self.adjacency_matrix=csr_matrix(infoOut["A"])
        self.kernel=np.array(infoOut["K"])

        self.n_components=None
        self.embedding=None
        self.reconstruction_error=None
        self.reconstruction_error_rel=None

        if not Mvu._library_instance:
            lib.terminate()

        finish=time.time()
        time_taken=round(finish-start, 2)

        if self.verbose:
            print(f"Execution of Mvu took {time_taken} seconds.")
            print("=================================================================")
        return self

    def transform(self, p):
        if self._Y is None:
            raise Exception("Call Mvu.fit prior to calling transform!")
        self.n_components=p
        self.embedding=self._Y[:, 0:p]
        cost_kmds=np.sum(self.eigenvalues[p:]**2)
        self.reconstruction_error=np.sqrt(cost_kmds)
        self.reconstruction_error_rel=self.reconstruction_error/np.sqrt(cost_kmds+np.sum(self.eigenvalues[:p]**2))
        return self.embedding

    def fit_transform(self, X, p):
        return self.fit(X).transform(p)

    def summary(self):
        print("=================================================================\n")
        print(f"Solver Summary:\n\nn_constraints={self.n_constraints}"+\
              f"\niter={self.iter}\nfeasratio={self.feasratio}"+\
              f"\nnumerr={self.numerr}\n")
        print(f"Mvu Summary:\n\ncost={self.cost}\nn_components={self.n_components}"+\
              f"\nerror_kmds={self.reconstruction_error}"+\
              f"\nrel_error_kmds={self.reconstruction_error_rel}\n")
        print("=================================================================")

