from preprocess import * 
import pandas as pd 


def create_graph_from_df(df): 

    """Function that takes in a DF and saves it as a connected graph with subjects, predicates, and objects. 
    These have to be defined by the user and it is not automated. 
    The output is a text file of these connections. 
    """
    df['Community Involvement'] = df['Community Involvement'].str.replace(r'\s*\([^)]*\)', '', regex=True).str.strip()
    df['Associated Communities'] = df['Associated Communities'].str.replace(r'\s*\([^)]*\)', '', regex=True).str.strip()
    # remove = 'Kind Community,'
    # df['Community Involvement'] = df['Community Involvement'].str.replace(remove, ' ', regex=False).str.replace(' +', ' ').str.strip()
    # df['Associated Communities'] = df['Associated Communities'].str.replace(remove, ' ', regex=False).str.replace(' +', ' ').str.strip()


    aloha_spirit = {
    'Almost always. Most people around me prioritize love, kindness, humility, respect, and community.': 'Almost Always',
     "Sometimes when I'm around the right people": 'Sometimes',
    'Almost half of the time  / on a sunny day': 'Half of the time'}

    df['Feel Aloha Spirit'] = df['Feel Aloha Spirit'].map(aloha_spirit)

    residence = {'Honolulu (Diamond Head, Hawaii Kai, Ala Moana, Kaimuki, Manoa, Palolo)': 'Honolulu',
       'Central Oahu (Waipahu, Pearl City, Miliani)' : 'Central Oahu',
       'North Shore (Haleiwa and Waimea)': 'North Shore', 'Windward Coast': 'East Side',
       'Leeward Coast': 'West Side'} 
    df['Residence'] = df['Residence'].map(residence)

    df_split_a = df['Community Involvement'].str.split(',', expand=True)
    
    # Optionally rename the new columns
    df_split_a.columns = ['involved_in_community_' + str(col) for col in df_split_a.columns] 
    
    df_split_b = df['Associated Communities'].str.split(',', expand=True)
    
    # Optionally rename the new columns
    df_split_b.columns = ['associated_community_' + str(col) for col in df_split_b.columns]
    
    # # Combine with original DataFrame if desired
    df_com = pd.concat([df[['Main Community', 'Community Involvement', 'Community Scale', 'Feel Aloha Spirit', 'Hawaiian Culture', 'Years on Island:', 'Education', 'Gender', 'Religious View', 'Age',  'Occcupation', 'State', 'Residence']], df_split_a, df_split_b], axis=1)



    com_inv =  []
    assoc_com = []
    for _, row in df_com.iterrows():
        for col in df_split_a.columns: 
            if (row[col] == None) | (row[col] == np.nan): 
                print('nothing found in involved com -- skipping')
    
            elif row['Main Community'] == row[col]: 
                print('Main col == involved com -- skipping')
                
            else: 
                com_inv.append((row["Main Community"], "also_involved_in", row[col]))
            
        for col in df_split_b.columns:
            if (row[col] == None) | (row[col] == np.nan): 
                print('nothing found in associated com -- skipping')
            elif row['Main Community'] == row[col]: 
                print('Main col == associated com -- skipping')
            else: 
                com_inv.append((row["Main Community"], "associated_with", row[col]))
    
        com_inv.append((row['Main Community'], "has_the_gender", row['Gender']))
        com_inv.append((row['Main Community'], "level_of_involvement", row['Community Scale']))
        com_inv.append((row['Feel Aloha Spirit'], "level_of_involvement", row['Community Scale']))
        com_inv.append((row['Main Community'], "feels_aloha_spirit", row['Feel Aloha Spirit']))
    
        com_inv.append((row['Feel Aloha Spirit'], "hawaiian_culture_knowledge", row['Hawaiian Culture']))
    
        com_inv.append((row['Main Community'], "has_education_level", row['Education'])) 
    
        com_inv.append((row['Main Community'], "has_religious_view", row['Religious View'])) 
    
        # com_inv.append((row['Main Community'], "in_age_rage_of", row['Age'])) 
    
        # com_inv.append((row['Main Community'], "years_on_island", row['Years on Island: '])) 
    
        
        com_inv.append((row['Main Community'], "lives_in", row['Residence'])) 
    
        com_inv.append((row['Main Community'], "originally_from", row['State'])) 
    
        com_inv.append((row['State'], "has_education_level", row['Education'])) 


        relationships = []

        # Ensure same number of columns in both DataFrames
        min_cols = min(df_split_a.shape[1], df_split_b.shape[1])
        
        for i in range(len(df_split_a)):  # iterate over rows
            for j in range(min_cols):     # iterate over matching columns
                a_val = df_split_a.iloc[i, j]
                b_val = df_split_b.iloc[i, j]
                
                # skip if either value is missing or empty
                if pd.notna(a_val) and pd.notna(b_val) and a_val.strip() and b_val.strip():
                    relationships.append((a_val.strip(), 'is_friends_with', b_val.strip()))
            
        # com_inv.append((row['State'], "years_on_island", row['Years on Island: '])) 

        with open('data/kg_pairs_list.txt', 'w') as f:
            for item in com_inv:
                f.write(f"{item}\n")

        print(f'saved {len(com_inv)} pairs to .txt file')