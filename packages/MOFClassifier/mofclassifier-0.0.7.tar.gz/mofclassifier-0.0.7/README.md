## MOFClassifier: A Machine Learning Approach for Validating Computation-Ready Metal-Organic Frameworks.
                                                                                                                                          
![GitHub repo size](https://img.shields.io/github/repo-size/sxm13/MOFClassifier?logo=github&logoColor=white&label=Repo%20Size)
[![Requires Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg?logo=python&logoColor=white)](https://python.org/downloads)
[![GitHub license](https://img.shields.io/github/license/mtap-research/MOFClassifier)](https://github.com/mtap-research/MOFClassifier/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15654431.svg)](https://doi.org/10.5281/zenodo.15654431)
                         
**Developed by:** [Guobin Zhao](https://github.com/sxm13)               
                                                  
### Installation 
                                     
```sh
pip install MOFClassifier
```

### Examples                                                                                                     
```python
from MOFClassifier import CLscore
result = CLscore.predict(root_cif="./example.cif")
```
-  **root_cif**: the path of your structure
-  **result**: a. cifid: the name of structure; b. all_score: the CLscore predicted by 100 models (bags); c. mean_score: the mean CLscore of CLscores                                                 

```python
from MOFClassifier import CLscore
results = CLscore.predict_batch(root_cifs=["./example1.cif""./example2.cif","./example3.cif"])
```
-  **root_cifs**: the path of your structures
-  **results**: a. cifid: the name of structure; b. all_score: the CLscore predicted by 100 models (bags); c. mean_score: the mean CLscore of CLscores   

### Citation                                          
**Guobin Zhao**, **Pengyu Zhao** and **Yongchul G. Chung**. 2025. **arXiv.2506.14845**.
