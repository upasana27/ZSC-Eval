import os, shutil
import json
folder_path = "./questionnaire"
flag = 0
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as file:
            try:
                
                data = json.load(file)
                for key in data:
                    if key == 'in_game':
                        # print(len(data[key]))
                        for trajectory in data[key]:
                            traj_id = trajectory['traj_path']
                            traj_algo = trajectory['teammate']
                            # find trajectory with that id
                            traj_path = "trajs/"
                            for fname in os.listdir('./' + traj_path):
                                if traj_id == traj_path + fname:
                                    # print("found", flag)
                                    # move the trajectory to that algo path
                                    if traj_algo == 'FCP':
                                        print("here at fcp")
                                        mv_path = "./fcp/"
                                        shutil.copy(traj_path + fname, mv_path)

                                    elif traj_algo == 'PBT':
                                        print("here at pbt")
                                        mv_path = "./hsp/"
                                        shutil.copy(traj_path + fname, mv_path)
                                    elif traj_algo == 'MEP':
                                        print("here at mep")
                                        mv_path = "./mep/"
                                        shutil.copy(traj_path + fname, mv_path)
                                    elif traj_algo == 'COLE':
                                        print("here at cole")
                                        mv_path = "./cole/"
                                        shutil.copy(traj_path + fname, mv_path)
            except json.JSONDecodeError as e:
                print("Error reading {filename} : {e}")