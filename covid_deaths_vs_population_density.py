import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests, re
import seaborn as sns
import matplotlib.gridspec as gridspec
import os   

import_popdens_df = pd.read_csv('data/API_EN.POP.DNST_DS2_en_csv_v2_2446063/API_EN.POP.DNST_DS2_en_csv_v2_2446063.csv', skiprows=4)
year = '2018'
popdens_df = import_popdens_df[~import_popdens_df[year].isna()][['Country Name',year]]
popdens_df = popdens_df.rename(columns={year: 'Population density','Country Name': 'Country'})

html_source = requests.get('https://www.worldometers.info/coronavirus/#countries').text
html_source = re.sub(r'<.*?>', lambda g: g.group(0).upper(), html_source)
import_deaths_df = pd.read_html(html_source)
deaths_df = import_deaths_df[0]

deaths_df = deaths_df.rename(columns={'Country,Other':'Country','Deaths/1M pop':'Deaths per million'})[['Country', 'Deaths per million','Population','Continent']]
deaths_df = deaths_df.dropna()
not_countries=['North America','Asia','South America','Europe','Africa','Oceania','World','Total:']
deaths_df = deaths_df[ ~deaths_df['Country'].isin(not_countries) ]
df=pd.merge(how='inner',left=deaths_df,right=popdens_df,on='Country')
df=df[df['Population density']<500]

def plot_continent(df, continent):
    df_continent = df[df['Continent']==continent]
    plt.figure(figsize=(10,10))
    plt.tight_layout()
    gspec = gridspec.GridSpec(ncols=8, nrows=8)
    #sns.set_palette('husl')

    top_hist = plt.subplot(gspec[0:3, :-3])
    scatter = plt.subplot(gspec[3:, :-3])
    right_hist = plt.subplot(gspec[3:, -3:])
    kwargs = {'data':df_continent,
               'element':"step", 
               'fill':False,
               'legend':False}
    sns.histplot(y='Deaths per million',
                 ax=right_hist,
                 **kwargs)
    sns.histplot(x='Population density',
                 ax=top_hist,
                 **kwargs)

    sns.scatterplot(data=df_continent,
                    x='Population density',
                    y='Deaths per million',
                    ax=scatter,
                    alpha=0.7,
                    s=30,
                    size='Population',
                    sizes=(20,800),
                    legend='brief')

    # scatter.legend(bbox_to_anchor=(1.4,1.5),frameon=False)


    right_hist.get_xaxis().set_visible(False)
    top_hist.get_xaxis().set_visible(False)
    right_hist.get_yaxis().set_visible(False)
    top_hist.get_yaxis().set_visible(False)
    plt.gcf().suptitle("{}\nCovid-19 deaths per million vs. population density\nwith distributions".format(continent))

    for ax in plt.gcf().get_axes():
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
    
    dir_name = './out/'
    file_name = 'covid19_deaths_per_million_vs_pop_dens_{}.png'.format(continent.replace("/","-"))

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    plt.savefig(dir_name + file_name)
    print("Saved: {}".format(dir_name + file_name))

continent_order=['Africa','Asia','Australia/Oceania','Europe','North America','South America']
for continent in continent_order:
    plot_continent(df,continent)
