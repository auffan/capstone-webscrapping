from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    url_get= requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
    soup = BeautifulSoup(url_get.content,"html.parser")
    table = soup.find('div', attrs={'class':'lister-list'})
    table1 = soup.find_all('div', attrs={'lister-item-content'})

    temp = []
    table1 = table.find_all('div', attrs={'lister-item-content'})

    for i in range(0, len(table1)):
        table1 = table.find_all('div', attrs={'lister-item-content'})[i]
        judul = table1.find_all('h3')[0].find_all('a')[0].text
        skor = table1.find_all('div','inline-block ratings-imdb-rating')[0].find_all('strong')[0].text
        votes = table1.find_all('p','sort-num_votes-visible')[0].find('span',attrs={'name':'nv'}).text
        try:meta = table1.find_all('div','inline-block ratings-metascore')[0].find_all('span')[0].text.strip()
        except IndexError:meta = 0

        temp.append([judul,meta,skor,votes])

    temp

    df = pd.DataFrame(temp, columns=('Judul','Meta','Rating','Votes'))
    df['Meta']=df['Meta'].astype('int')
    df['Rating']=df['Rating'].astype('float')
    df['Votes'] = df['Votes'].replace('[^\d.]+', '', regex=True)
    df['Votes']=df['Votes'].astype('int')
    df.set_index('Judul', inplace=True)
    df = df.sort_values('Votes',ascending=False).head(7)
    df


    return df

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df["Votes"].plot(kind="barh")
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()