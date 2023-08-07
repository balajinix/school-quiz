# Quiz

## dev env

conda create -n nafl python=3.9.16 anaconda  
conda activate nafl 
pip install -r requirements.txt  
python app.py  

## docker

sudo docker build -t nafl-quiz .  
sudo docker run -d -p 7860:7860 nafl-quiz

