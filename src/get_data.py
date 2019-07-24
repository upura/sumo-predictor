import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


OUTPUT_DIR = 'data'


def fetch_data(yyyy, mm, d):

    URL = f'http://sumodb.sumogames.de/Results.aspx?b={yyyy}{mm}&d={d}'
    html = requests.get(URL)
    soup = BeautifulSoup(html.text, "html.parser")
    soup = soup.find('table', class_="tk_table")
    
    east_result = soup.find_all("td", class_="tk_kekka")
    east_wrestler = soup.find_all("td", class_="tk_east")
    west_wrestler = soup.find_all("td", class_="tk_west")
    
    result = [er.find('img')['src'] for er in east_result]

    # mapping
    result_dict = {
         'img/hoshi_shiro.gif': 1,
         'img/hoshi_fusensho.gif': 1, 
         'img/hoshi_kuro.gif': 0,
         'img/hoshi_fusenpai.gif': 0
    }

    result = [result_dict[r] for r in result]
    
    east_result = result[0::2]
    west_result = result[1::2]

    east_wrestler = [ew.find('a')['title'].split(",")[0] for ew in east_wrestler]
    west_wrestler = [ww.find('a')['title'].split(",")[0] for ww in west_wrestler]

    if d!=15:
        res = pd.DataFrame({
            'wrestler': east_wrestler + west_wrestler,
            f'day_{d}': east_result + west_result
        })
    else:
        res = pd.DataFrame({
            'wrestler': east_wrestler + west_wrestler,
            f'day_{d}': east_result + west_result,
            'final_opponent': west_wrestler + east_wrestler
        })

    return res


if __name__ == '__main__':
    for yyyy in range(2000, 2020):
        for mm in range(1, 13, 2):
            mm = str(mm).rjust(2, '0')
            
            try:
                df = fetch_data(yyyy, mm, 1)

                for d in range(2, 16):
                    _df = fetch_data(yyyy, mm, d)
                    df = pd.merge(df, _df, on='wrestler', how='left')    
                    time.sleep(3)

                df['datetime'] = str(yyyy) + str(mm)
                df.to_csv(f'{OUTPUT_DIR}/df_{yyyy}{mm}.csv', index=False, encoding='utf-8-sig')

            except:
                pass
