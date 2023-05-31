library(Arothron)
library(Morpho)
library(geomorph)

#Load sample 3d landmark data from Arothron
data("Lset3D_array")

#Run a gpa based on the sample data and get the gpa aligned landmark data
gpa<-procSym(Lset3D_array)
gpa_coords<-gpa$orpdata

#Calculate pairwise Procrustes distance matrix
gpa_coords_2d <- two.d.array(gpa_coords)
procDists_matrix <- as.matrix(dist(gpa_coords_2d))

#Convert Procrustes distance matrix to an vector
#Because the distance matrix is symmetrical along the diagnol elements,
#Only half of the matrix is needed to get all pairwise distances
proc_dists <- NULL
for (i in 1:(dim(procDists_matrix)[1]-1)){
  for (j in 1:(dim(procDists_matrix)[1] - i)){
    proc_dists <- append(proc_dists, procDists_matrix[i, j+i])
  }
}

#PC score matrix
pcScores_mat <- gpa$PCscores

#calculate pairwise distance matrix based on all PC scores
pca_dists_mat<-as.matrix(dist(pcScores_mat))

#Convert pc score distance matrix to a vector
#Again, the distance matrix is symmetrical along the diagnol
#Only half of the matrix is needed to get all pairwise distances
pca_dists <- NULL
for (i in 1:(dim(pca_dists_mat)[1]-1)){
  for (j in 1:(dim(pca_dists_mat)[1] - i)){
    pca_dists <- append(pca_dists, pca_dists_mat[i, j+i])
  }
}

#Plot Procrustes distances and distances based on all PC scores
plot(proc_dists, pca_dists)
abline(coef=c(0,1))


#calculate correlation
cor.test(proc_dists, pca_dists)
