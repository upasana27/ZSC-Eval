import csv,sys
import pandas as pd
layout = sys.argv[1]
agent = sys.argv[2]
df = pd.read_csv("HA_subj_results.csv")
df = df.loc[lambda df:df["layout"] == str(layout) ]
df1 = df.loc[lambda df:df["agent1"] == str(agent)]

df1.columns = [
               'layout',
               'agent0',
               'agent1',
                'total_subtasks_p1',
               'dep_subtasks_p1',
               'triggered_subtasks_p1',
               'accepted_triggered_subtasks_p1',
               'total_subtasks_p2', 
               'dep_subtasks_p2', 
               'triggered_subtasks_p2', 
               'accepted_triggered_subtasks_p2', 
               'timestep'
             ]
df1 = df1[['total_subtasks_p1',
            'dep_subtasks_p1',
            'triggered_subtasks_p1',
            'accepted_triggered_subtasks_p1',
            'total_subtasks_p2', 
            'dep_subtasks_p2', 
            'triggered_subtasks_p2', 
            'accepted_triggered_subtasks_p2', 
            'timestep'
            ]]
print(df1.mean())
# with open("HA_subj_results.csv", 'r', newline = '') as file:


# with open("HA_obj_results.csv", 'w', newline = '') as file:
#     writer = csv.writer(file)
#     field = ['agent0', 'agent1', 'p1_r', 'p1_g', 'p2_r', 'p2_g', 'p1_events', 'p2_events' ]
#     writer.writerow(field)
# with open("HA_subj_results.csv", 'w', newline = '') as file:
#     writer = csv.writer(file)
#     field = ['agent0',
#              'agent1', 
#              'timestep',
#              'total_subtasks_p1', 
#              'total_subtasks_p2', 
#              'total_dep_subtasks_p1', 
#              'total_dep_subtasks_p2',
#              'total_triggered_subtasks_p1', 
#              'total_triggered_subtasks_p2', 
#              'total_accepted_triggered_subtasks_p1', 
#              'total_accepted_triggered_subtasks_p2' 
#              ]
#     writer.writerow(field)