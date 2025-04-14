
import pickle
with open("traj_0_1.pkl", 'rb') as f:
        data = pickle.load(f)
print(data)
p1_action_traj = []
p2_action_traj = []
p1_state_traj = []
p2_state_traj = []
p1_events_traj = []
p2_events_traj = []
agent_idx_traj = []
for i in range(0, len(data)):
        if i % 4 == 0 :
                p1_state_traj.append(data[i]["players"][0])
                p2_state_traj.append(data[i]["players"][1])
                if i + 1 < len(data):
                        agent_idx_traj.append(data[i+1])
                if i + 2 < len(data):
                        p1_action_traj.append(data[i+2][0])
                        p2_action_traj.append(data[i+2][1])
                if i + 3 < len(data):
                        p1_events_traj.append(data[i+3][0])
                        p2_events_traj.append(data[i+3][1])
print(agent_idx_traj)