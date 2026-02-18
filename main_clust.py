# Aplicatie clusterizare ierarhica
# Outputuri grafice:
# Dendrograma
# Plot partitie
# Plot Silhouette
# Histograme
# Output tabel: componenta partitiilor si indecsii Silhouette la nivel de instante
import geopandas
import pandas as pd
from scipy.cluster.hierarchy import linkage,leaves_list
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, silhouette_samples
from geopandas import GeoDataFrame
from sklearn.preprocessing import StandardScaler

from functii import *
from grafice import *



set_date = pd.read_csv("date.csv", index_col=0)
variabile = list(set_date)


fisier_harta = geopandas.read_file('110m_cultural/ne_110m_admin_0_countries.shp')
camp_legatura = "NAME"



valori_lipsa = set_date.isna().any().any()
if valori_lipsa:
    nan_replace(set_date)

raw_values=set_date[variabile].values
scaler=StandardScaler()
x = scaler.fit_transform(raw_values)

metoda = "ward"
h = linkage(x, method=metoda)
t_h = pd.DataFrame(h,columns=["Cluster 1","Cluster 2","Distanta","Frecventa"])
t_h.index.name="Numar Jonctiune"
t_h.to_csv("out/Ierarhie.csv")

plot_ierarhie(h,0,"Graficul Ierarhie",0,set_date.index)
show()

n = len(set_date)

clusteri_singleton = leaves_list(h)
# Calcul si analiza partitie optimala
k_opt, threshold_opt, p_opt = partitie(h)
# Calcul scor Silhouette la nivel de partitie
silhouette_opt = silhouette_score(x, p_opt)
# Calcul scor Silhouette la nivel de instante
index_silhouette_opt = silhouette_samples(x, p_opt)

culori = generare_rampa("rainbow", k_opt)


culori_instante=[]
for i in range(n):
    index_cluster = int(p_opt[clusteri_singleton[i]][1:])-1
    culori_instante.append(culori[index_cluster])

culori_dendrograma = unique(culori_instante)

plot_ierarhie(h, threshold_opt,
              "Plot ierarhie - partitia optimala. Scor Silhouette:" + str(silhouette_opt),
              k_opt, set_date.index, culori=culori_dendrograma)

# Creare tabel de partitii in care sunt salvate partitiile
t_partitii = pd.DataFrame({
    "P_opt": p_opt,
    "Scor Silhouette P_opt": index_silhouette_opt
}, index=set_date.index)

# Trasare grafic Silhouette
f_plot_silhouette(p_opt,index_silhouette_opt,silhouette_opt,
                  culori,"Plot Silhouette. Metoda " + metoda)

# Calcul axe principale pentru trasare plot partitie
pca = PCA(2)
pca.fit(x)
tz = pd.DataFrame(pca.transform(x), set_date.index, ["z1", "z2"])

# Plot partitie in axele principale
plot_scoruri(tz, "z1", "z2", p_opt, clase=np.unique(p_opt),
             titlu="Plot partitie optimala", etichete=True, culori=culori)

# Trasare histograme pentru partitia optimala
for variabila in variabile:
    histograme(set_date, variabila, p_opt, culori)

if fisier_harta is not None:
    harta_shp = fisier_harta.copy()
    print(list(harta_shp))
    harta(harta_shp, camp_legatura, t_partitii,
          "P_opt", "Partitia optimala", culori)

show()

# Calcul si analiza partitie cu k clusteri
# Exemplu pe partitia de 5 clusteri
k = 5
k, threshold_k, p_k = partitie(h, k)
silhouette_k = silhouette_score(x, p_k)
index_silhouette_p_k = silhouette_samples(x, p_k)
culori = generare_rampa("rainbow", k)
culori_instante=[]
for i in range(n):
    culori_instante.append(culori[int(p_k[clusteri_singleton[i]][1:])-1])
culori_dendrograma = unique(culori_instante)

plot_ierarhie(h, threshold_k, "Plot ierarhie cu " + str(k) + " clusteri. Scor Silhouette:"+str(silhouette_k), k,
              set_date.index,culori_dendrograma)
t_partitii["P_" + str(k)] = p_k
t_partitii["Scor Silhouette P_"+str(k)]=index_silhouette_p_k
f_plot_silhouette(p_k,index_silhouette_p_k,silhouette_k,
                  culori,"Plot Silhouette. Metoda " + metoda)
plot_scoruri(tz, "z1", "z2", p_k, clase=np.unique(p_k),
             titlu="Plot partitie cu " + str(k) + " clusteri. Scor Silhouette:"+str(silhouette_k), etichete=True, culori=culori)

for variabila in variabile:
    histograme(set_date, variabila, p_k, culori)
if fisier_harta is not None:
    harta_shp = fisier_harta.copy()
    harta(harta_shp, camp_legatura, t_partitii,
          "P_"+str(k), "Partitia din "+str(k)+" clusteri", culori)

# Salvare partitii
t_partitii.to_csv("out/Partitii.csv")

show()
