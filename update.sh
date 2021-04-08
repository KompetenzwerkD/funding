. ~/miniconda3/etc/profile.d/conda.sh
conda activate smw
python build.py
git add .
git commit -m "site update"
git push -u origin main