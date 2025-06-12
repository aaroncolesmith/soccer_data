import pandas as pd
import requests
import re
import functools as ft
import numpy as np
from bs4 import BeautifulSoup


def extract_league_from_url(url):
    """
    Extracts the league name from a given Fbref match URL.

    The league name is expected to be the last part of the URL path,
    following the four-digit year (e.g., '2025-Major-League-Soccer').

    Args:
        url (str): The URL of the match page.

    Returns:
        str or None: The extracted league name (e.g., 'Major-League-Soccer'),
                     or None if the pattern is not found.
    """
    if not isinstance(url, str):
        return None # Handle non-string inputs gracefully

    # Get the last segment of the URL path (e.g., 'New-York-City-FC-New-York-Red-Bulls-May-17-2025-Major-League-Soccer')
    path_segment = url.split('/')[-1]

    # Use a regular expression to find the pattern:
    # \d{4}   - Matches exactly four digits (for the year)
    # -       - Matches a literal hyphen
    # ([a-zA-Z0-9-]+) - This is the capturing group:
    #                   [a-zA-Z0-9-] - Matches any alphanumeric character or a hyphen
    #                   +            - Matches one or more of the preceding characters
    # $       - Asserts position at the end of the string
    # This regex specifically looks for the league name that appears directly
    # after the four-digit year and a hyphen at the very end of the URL segment.
    match = re.search(r'\d{4}-([a-zA-Z0-9-]+)$', path_segment)

    if match:
        # If a match is found, return the content of the first capturing group,
        # which is the league name.
        return match.group(1)
    else:
        # If no match is found, return None. This could happen if the URL
        # format deviates from the expected pattern.
        return None

def get_match_box_score(r,match_url):
    """
    Fetches the match box score from the given URL.
    
    Parameters:
    match_url (str): The URL of the match box score page.
    Returns:
    pd.DataFrame: A DataFrame containing the match statistics.
    """

    # r = requests.get(match_url)


    soup = BeautifulSoup(r.content, 'html.parser')

    team_one = soup.select("#content > div.scorebox > div:nth-child(1) > div:nth-child(1) > strong > a")
    team_one=team_one[0].text

    team_two = soup.select("#content > div.scorebox > div:nth-child(2) > div:nth-child(1) > strong > a")
    team_two=team_two[0].text

    table_num = len(pd.read_html(r.content))

    if table_num == 20:
        dfs_one = [pd.read_html(r.content)[3],pd.read_html(r.content)[4],pd.read_html(r.content)[5],pd.read_html(r.content)[6],pd.read_html(r.content)[7],pd.read_html(r.content)[8]]
    elif table_num == 7:
        dfs_one = [pd.read_html(r.content)[3]]
    else:
        print(f'Unexpected number of tables: {table_num} in {match_url}')
        with open('data/error_log.txt', 'a') as f:
            f.write(f'Unexpected number of tables: {table_num} in {match_url}\n')
        with open('data/error_matches.txt', 'a') as f:
            f.write(f'{match_url}\n')
    

    d1 = ft.reduce(lambda left, right: pd.merge(left, right, how='inner'), dfs_one).copy()
    d1.columns=d1.columns.map('_'.join).str.strip().str.lower().str.replace('%','_pct').str.replace(' ','_')
    for i in range(0,50):
        d1.columns=d1.columns.str.replace('unnamed:_'+str(i)+'_level_0_','')
    d1=d1.loc[d1.pos.notnull()].copy()
    d1['team'] = team_one

    if table_num == 20:
        dfs_two = [pd.read_html(r.content)[10],pd.read_html(r.content)[11],pd.read_html(r.content)[12],pd.read_html(r.content)[13],pd.read_html(r.content)[14],pd.read_html(r.content)[15]]
    if table_num == 7:
        dfs_two = [pd.read_html(r.content)[5]]

    d2 = ft.reduce(lambda left, right: pd.merge(left, right, how='inner'), dfs_two).copy()
    d2.columns=d2.columns.map('_'.join).str.strip().str.lower().str.replace('%','_pct').str.replace(' ','_')
    for i in range(0,50):
        d2.columns=d2.columns.str.replace('unnamed:_'+str(i)+'_level_0_','')
    d2=d2.loc[d2.pos.notnull()].copy()
    d2['team'] = team_two

    d=pd.concat([d1,d2]).reset_index(drop=True)

    d.rename(columns={
            "performance_gls":"goals",
            "performance_ast":"assists",
            "performance_pk":"pks",
            "performance_pkatt":"pk_att",
            "performance_sh":"shots",
            "performance_sot":"shots_on_goal",
            "performance_crdy":"yellow_card",
            "performance_crdr":"red_card",
            "performance_touches":"touches",
            "performance_tkl":"tackles",
            "performance_int":"ints",
            "performance_blocks":"blocks",
            "expected_xg":"xg",
            "expected_npxg":"npxg",
            "expected_xag":"xag",
            "sca_sca":"sca",
            "sca_gca":"gca",
            "passes_cmp":"passes_cmp",
            "passes_att":"passes_att",
            "passes_cmp_pct":"passes_cmp_pct",
            "passes_prgp":"progressive_passes",
            "carries_carries":"carries",
            "carries_prgc":"progressive_carries",
            "take-ons_att":"take_ons_attempted",
            "take-ons_succ":"take_ons_successful",
            "total_cmp":"del_asd",
            "total_att":"del_dd",
            "total_cmp_pct":"del_cmp",
            "total_totdist":"passing_distance",
            "total_prgdist":"progressive_passing_distance",
            "short_cmp":"short_passes_cmp",
            "short_att":"short_passes_att",
            "short_cmp_pct":"short_passes_cmp_pct",
            "medium_cmp":"med_passes_cmp",
            "medium_att":"med_passes_att",
            "medium_cmp_pct":"med_passes_cmp_pct",
            "long_cmp":"long_passes_cmp",
            "long_att":"long_passes_att",
            "long_cmp_pct":"long_passes_cmp_pct",
            "ast":"del_ast",
            "xag":"del_xag",
            "xa":"xa",
            "kp":"key_passes",
            "1/3":"final_third_passes",
            "ppa":"passes_penalty_area",
            "crspa":"crosses_penalty_area",
            "prgp":"del_prgp",
            "att":"del_att",
            "pass_types_live":"live_ball_passes",
            "pass_types_dead":"dead_ball_passes",
            "pass_types_fk":"fk_passes",
            "pass_types_tb":"through_balls",
            "pass_types_sw":"switches",
            "pass_types_crs":"crosses",
            "pass_types_ti":"throw_ins",
            "pass_types_ck":"corners",
            "corner_kicks_in":"corners_inswing",
            "corner_kicks_out":"corners_outswing",
            "corner_kicks_str":"corners_straight",
            "outcomes_cmp":"del_pass_com",
            "outcomes_off":"offside_passes",
            "outcomes_blocks":"blocked_passes",
            "tackles_tkl":"del_tackles_tkl",
            "tackles_tklw":"tackles_won",
            "tackles_def_3rd":"tackles_def_3rd",
            "tackles_mid_3rd":"tackles_mid_3rd",
            "tackles_att_3rd":"tackles_att_3rd",
            "challenges_tkl":"dribblers_tackled",
            "challenges_att":"dribblers_challenged",
            "challenges_tkl_pct":"tackle_pct",
            "challenges_lost":"challenges_lost",
            "blocks_blocks":"del_blocks_blocks",
            "blocks_sh":"block_shot",
            "blocks_pass":"block_pass",
            "int":"del_int",
            "tkl+int":"tkl+int",
            "clr":"clearances",
            "err":"errors",
            "touches_touches":"del_touches_touches",
            "touches_def_pen":"touches_def_pen",
            "touches_def_3rd":"touches_def_3rd",
            "touches_mid_3rd":"touches_mid_3rd",
            "touches_att_3rd":"touches_att_3rd",
            "touches_att_pen":"touches_att_pen",
            "touches_live":"touches_live_ball",
            "take-ons_succ_pct":"take_ons_succ_pct",
            "take-ons_tkld":"take_ons_tackled",
            "take-ons_tkld_pct":"take_ons_tkld_pct",
            "carries_totdist":"carries_total_distance",
            "carries_prgdist":"carries_progressive_distance",
            "carries_1/3":"carries_third",
            "carries_cpa":"carries_into_penalty_area",
            "carries_mis":"carries_mis",
            "carries_dis":"carries_dis",
            "receiving_rec":"passes_received",
            "receiving_prgr":"progressive_passes_received",
            "performance_2crdy":"del_performance_2crdy",
            "performance_fls":"fouls_committed",
            "performance_fld":"fouls_drawn",
            "performance_off":"offsides",
            "performance_crs":"del_performance_crs",
            "performance_tklw":"del_performance_tklw",
            "performance_pkwon":"pk_won",
            "performance_pkcon":"pk_conceded",
            "performance_og":"own_goals",
            "performance_recov":"balls_recovered",
            'player':'Player'
        },
                inplace=True)


    for x in d.columns:
        if 'del_' in x:
            del d[x]

    num_cols=[]
    non_num_cols=[]
    for col in d.columns:
        if col in ['first_game','last_game']:
            try:
                d[col]=pd.to_datetime(d[col])
            except:
                pass
        else:
            try:
                d[col] = pd.to_numeric(d[col])
                num_cols.append(col)
            except:
                # print(f'{col} failed')
                non_num_cols.append(col)

    if 'number' in num_cols:
        num_cols.remove('number')
    else:
        num_cols.remove('#')

    d['match_url'] = match_url
    return d

df = pd.read_parquet('https://github.com/aaroncolesmith/data_action_network/raw/refs/heads/main/data/fb_ref_data.parquet', engine='pyarrow')
d = pd.read_parquet('data/fb_ref_data_box_scores.parquet', engine='pyarrow')

# Apply the function to the 'url' column to create the new 'league' column
df['league'] = df['url'].apply(extract_league_from_url)



with open('data/error_matches.txt', 'r') as file:
    error_matches = file.readlines()
    error_matches = [line.strip() for line in error_matches]

## lets get the list of matches that we have not yet scraped
## first we'll get the list of matches in the league_list
league_list_one = ['Serie-A', 'Premier-League', 'La-Liga', 'Bundesliga']
league_list_two = ['FA-Cup','Championship','Major-League-Soccer','Eredivisie','Ligue-1','Liga-MX','Liga-Portuguesa','Scottish-Premier-League','UEFA-Champions-League','UEFA-Europa-League']
league_list_three = ['Champions-League','Copa-del-Rey','Conference-League','Europa-League','UEFA-Super-Cup','Coppa-Italia','DFB-Pokal','Saudi-Professional-League','Friendlies-M']
league_list_four = ['World-Cup',]

league_list = league_list_one + league_list_two + league_list_three

match_url_list_all = df.loc[df['league'].isin(league_list),'url'].unique().tolist()

## remove the matches that have already been scraped
match_urls_already_scraped = d['match_url'].unique().tolist()

match_urls_to_scrape = [url for url in match_url_list_all if url not in match_urls_already_scraped and url not in error_matches]

print(f"Number of matches to scrape: {len(match_urls_to_scrape)}")

## if we estimate that each match takes about 8 seconds to scrape, we can estimate the total time it will take to scrape all matches
total_time_estimate = len(match_urls_to_scrape) * np.random.uniform(6.2, 10.1)
print(f"Estimated total time to scrape all matches: {total_time_estimate / 60:.2f} minutes")

for match_url in match_urls_to_scrape:
    #sleep for random time between 6.2 and 10.1 seconds
    time.sleep(np.random.uniform(6.2, 10.1))
    r = requests.get(match_url)
    if r.status_code == 200:
        try:
            match_df = get_match_box_score(r, match_url)
            print(f"Fetched data for match  {match_url}")
            d = pd.concat([d, match_df], ignore_index=True)
        except Exception as e:
            print(f"Error processing match {match_url}: {e}")
            continue
    else:
        print(f"Failed to fetch data from {match_url}. Status code: {r.status_code}")
        timeout = r.headers.get('Retry-After', 5)  # Default to 5 seconds if not specified
        print(f"Retrying after {timeout} seconds...")
        import time
        time.sleep(int(timeout))
        r = requests.get(match_url)
        if r.status_code == 200:
            match_df = get_match_box_score(r, match_url)
            print(f"Fetched data for match on {match_url}")
            d = pd.concat([d, match_df], ignore_index=True)
        else:
            print(f"Failed again. Status code: {r.status_code}")

d.to_parquet('data/fb_ref_data_box_scores.parquet', index=False, engine='pyarrow')

