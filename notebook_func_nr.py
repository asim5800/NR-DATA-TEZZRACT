#!/usr/bin/env python
# coding: utf-8

#


import pandas as pd
import numpy as np
import requests
import pandas as pd
from io import BytesIO
import pandas as pd
import numpy as np
import itertools
from datetime import datetime
import re



def process_input(df: pd.DataFrame):
   



    # In[2]:


    df.head()


    # In[3]:


    # Filter only Andheri rows
    df_andheri = df[df['location'] == "Andheri"].copy()

    # Update Lot column: keep "Fresh Data", else "-"
    df_andheri['Lot'] = df_andheri['Lot'].apply(lambda x: x if x == "Fresh Data" else "-")



    df_andheri.head()


    # list all your mobile‑cols
    mobile_cols = [f'Mobile {i}' for i in range(1, 8)]

    def clean_mobile(x):
        # 1) to string, drop NaN
        s = str(x) if pd.notna(x) else ""
        # 2) strip non‑digits
        s = re.sub(r'\D', '', s)
        # 3) remove leading country/zero prefixes
        s = re.sub(r'^(?:91|0)', '', s)        # removes “91...” or “0...” at start
        # 4) if it still has >10 digits, take the last 10
        return s[-10:] if len(s) >= 10 else None

    # apply to every mobile column
    for col in mobile_cols:
        df_andheri[col] = df_andheri[col].apply(clean_mobile)

    # # (optional) flag any that still aren’t exactly 10 digits
    # for col in mobile_cols:
    #     df_andheri[f'{col}_valid'] = df_andheri[col].str.len() == 10

    df_andheri.head()


    # In[6]:


    df_andheri['TME Name 1'].info()


    # ─── Replace this with your actual “Anyone with link” URL + download=1 ───
    download_url = (
        "https://lightfintech-my.sharepoint.com/:x:/g/"
        "personal/asim_siddiqui_tezzract_com/"
        "Edq-lCn0a9VEuVGjkMk7-iIBlg1t7IuQiTmUiN4sINO3Xg"
        "?e=jHajak&download=1"
    )

    # 1) Fetch the .xlsx bytes  
    resp = requests.get(download_url)
    resp.raise_for_status()

    # 2) Wrap bytes in a buffer  
    buf = BytesIO(resp.content)

    # 3) Read only the IC sheet  
    df_cbi_tme = pd.read_excel(buf, sheet_name="CBI TME")

    # 4) Subset to just the columns you care about
    desired_cols = ['ID', 'TME NAME', 'TL', 'ASM', 'NR', 'Server']
    # Keep only those that actually exist
    keep = [c for c in desired_cols if c in df_cbi_tme.columns]
    df_cbi_tme = df_cbi_tme[keep]

    print("`CBI TME` sheet shape →", df_cbi_tme.shape)
    # print(df_ic_tme.head())


    # import time
    # import requests
    # import pandas as pd
    # from io import BytesIO

    # # ─── Base “Anyone with link” URL ───
    # base_url = (
    #     "https://lightfintech-my.sharepoint.com/:x:/g/"
    #     "personal/asim_siddiqui_tezzract_com/"
    #     "Edq-lCn0a9VEuVGjkMk7-iIBlg1t7IuQiTmUiN4sINO3Xg"
    # )

    # # append download and a timestamp to bust cache
    # download_url = f"{base_url}?download=1&nocache={int(time.time())}"

    # # 1) Fetch the bytes (no cache, follow redirects, browser UA)
    # headers = {
    #     'User-Agent':      'Mozilla/5.0',
    #     'Cache-Control':   'no-cache',
    #     'Pragma':          'no-cache',
    # }
    # resp = requests.get(download_url, headers=headers, allow_redirects=True)
    # resp.raise_for_status()

    # # 2) Wrap in buffer
    # buf = BytesIO(resp.content)

    # # 3) Read the “CBI TME” sheet explicitly with openpyxl
    # df_cbi_tme = pd.read_excel(buf, sheet_name="CBI TME", engine='openpyxl')

    # # 4) Keep only the columns you care about
    # desired_cols = ['ID', 'TME NAME', 'TL', 'ASM', 'NR', 'Server']
    # keep = [c for c in desired_cols if c in df_cbi_tme.columns]
    # df_cbi_tme = df_cbi_tme[keep]

    # print("`CBI TME` sheet shape →", df_cbi_tme.shape)



    df_cbi_tme.tail()

    # make sure the lookup DF has the exact column names you expect
    df_cbi_tme.columns = df_cbi_tme.columns.str.strip()  # strip stray spaces

    # build mapping dicts
    server_map = df_cbi_tme.set_index('TME NAME')['Server'].to_dict()
    hr_map     = df_cbi_tme.set_index('TME NAME')['NR'].to_dict()

    # map into your df_andheri
    df_andheri['Server']  = df_andheri['TME Name 1'].map(server_map)
    df_andheri['list_id'] = df_andheri['TME Name 1'].map(hr_map)


    # In[11]:


    df_andheri['TME Name 1'].info()




    df_andheri['Server'].info()


    # make a set of all valid names in your lookup
    valid_tmes = set(df_cbi_tme['TME NAME'].str.strip())

    # find the unique names in df_andheri that aren’t in valid_tmes
    bad_names = set(df_andheri['TME Name 1'].str.strip()) - valid_tmes
    print("These TME Name 1 values had no match:", bad_names)



    df_andheri['Server']  = df_andheri['Server'].astype(int)
    df_andheri['list_id'] = df_andheri['list_id'].astype(int)


    # In[16]:


    df_andheri.head()


    # In[17]:


    df_andheri['Server'].value_counts()



    # Update Lot column: keep "Fresh Data", else "-"
    df_andheri['Lot'] = df_andheri['Lot'].apply(lambda x: x if x == "Fresh Data" else "-")



    # list all your mobile‑cols
    mobile_cols = [f'Mobile {i}' for i in range(1, 8)]

    def clean_mobile(x):
        # 1) to string, drop NaN
        s = str(x) if pd.notna(x) else ""
        # 2) strip non‑digits
        s = re.sub(r'\D', '', s)
        # 3) remove leading country/zero prefixes
        s = re.sub(r'^(?:91|0)', '', s)        # removes “91...” or “0...” at start
        # 4) if it still has >10 digits, take the last 10
        return s[-10:] if len(s) >= 10 else None

    # apply to every mobile column
    for col in mobile_cols:
        df_andheri[col] = df_andheri[col].apply(clean_mobile)

    # # (optional) flag any that still aren’t exactly 10 digits
    # for col in mobile_cols:
    #     df_andheri[f'{col}_valid'] = df_andheri[col].str.len() == 10

    df_andheri.head()

 

    # In[21]:


    df_format = pd.read_excel(r"DAILER UPLOADED FORMAT.xlsx")


    # In[22]:


    df_final= df_andheri.copy()



    # 1) Keep your format‑template’s column order and add “Server” at the end:
    cols = df_format.columns.tolist() + ["Server"]

    # 2) Build an empty DataFrame with the same index (and length) as df_final:
    new_df = pd.DataFrame(index=df_final.index, columns=cols)

    # 3) Define the mapping from new_df cols → df_final cols:
    col_map = {
        "TL":                "Lot",
        "list_id":           "list_id",
        "phone_number":      "Mobile 1",
        "Business":          "BUSINESS",
        "Name":              "NAME",
        "Base Trade":        "Base Trade",
        "GST ":               "GST",
        "Location":          "City",
        "Tenor":             "Tenor",
        "Mobile3":           "Mobile 2",
        "Amount":            "Amount",
        "EMI":               "EMI",
        "Allocation":        "TME Name 1",
        "PF":                "PF",
        "Mobile2":           "Mobile 3",
        "Last feedback":     "Nature Of Business Activities",
        "Mobile4":           "Mobile 4",
        "Document required": "State",
        "Interest Rate":     "Rate",
        "Reaction":          "status",
        "1st Year EMI":      "Constitution Of Business",
        "list_id":           "list_id",
        "Server":            "Server",  # ← new mapping
        # leave others (source_id, phone_code, etc.) as NaN
    }

    # 4) Populate new_df by aligning on index:
    for dst, src in col_map.items():
        if src in df_final.columns:
            new_df[dst] = df_final[src].values

    # 5) (Optional) inspect
    print(new_df.head())
    print("Shape:", new_df.shape)




    # 1) Grab all columns that start with “Mobile”
    mobile_cols = [c for c in new_df.columns if c.lower().startswith('mobile')]

    # 2) Sort them by their numeric suffix (so Mobile2→Mobile3→Mobile4…)
    def _num(col):
        m = re.search(r'(\d+)', col)
        return int(m.group(1)) if m else float('inf')

    mobile_cols = sorted(mobile_cols, key=_num)

    # 3) Use a row-wise backward-fill across those columns, then take the first one
    first_mobile = new_df[mobile_cols].bfill(axis=1).iloc[:, 0]

    # 4) Fill phone_number where it’s null
    new_df['phone_number'] = new_df['phone_number'].fillna(first_mobile)

    # 5) Quick sanity check
    new_df['phone_number'].info()




# 1) Make a copy and name it rechurn
    nr = new_df.copy()

    # 2) Compute today's date string, e.g. "28 july"
    today    = datetime.now()
    date_str = today.strftime("%d %B").lower()

    # 3) Split by Server and write each to an in-memory buffer
    file_outputs = []
    for srv in nr['Server'].unique():
        df_sub = nr[nr['Server'] == srv].drop(columns=['Server'])

        buf = BytesIO()
        df_sub.to_excel(buf, index=False)
        buf.seek(0)

        fname = f"{date_str}_NR_server{int(srv)}.xlsx"
        file_outputs.append((fname, buf))

    # 4) Return just the list of (filename, buffer) tuples
    return file_outputs