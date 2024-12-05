
import pickle
with open("traj_0_1.pkl", 'rb') as f:
        data = pickle.load(f)
print(data[9])