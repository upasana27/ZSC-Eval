#!/bin/bash
env="Overcooked"

env="GRF"

# academy_3_vs_1_with_keeper
scenario=$1
num_agents=$3

algo="population"
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libffi.so.7

if [[ $2 == "fcp" ]];
then
    algorithm="fcp"
    exps=("fcp-S2-s9")
elif [[ $2 == "mep" ]];
then
    algorithm="mep"
    exps=("mep-S2-s9")
elif [[ $2 == "traj" ]];
then
    algorithm="traj"
    exps=("traj-S2-s9")
elif [[ $2 == "hsp" ]];
then
    algorithm="hsp"
    exps=("hsp-S2-s9")
elif [[ $2 == "cole" ]];
then
    algorithm="cole"
    exps=("cole-S2-s15")
else
    echo "bash eval_with_bias_agents.sh {scenario} {algo}"
    exit 0
fi

bias_agent_version="hsp"

declare -A LAYOUTS_KS
LAYOUTS_KS["academy_3_vs_1_with_keeper"]=3

path=../../policy_pool
export POLICY_POOL=${path}

K=$((2 * LAYOUTS_KS[${scenario}]))
bias_yml="${path}/${scenario}/hsp/s1/${bias_agent_version}/benchmarks-s${K}.yml"
yml_dir=eval/eval_policy_pool/${scenario}/results/
mkdir -p ${yml_dir}

n=$(grep -o -E 'bias.*_(final|mid):' ${bias_yml} | wc -l)
echo "Evaluate ${scenario} with ${n} agents"
population_size=$((n + 1))

ulimit -n 65536

len=${#exps[@]}
for (( i=0; i<$len; i++ )); do
    exp=${exps[$i]}

    echo "Evaluate population ${algo} ${exp} ${population}"
    for seed in $(seq 1 3); do
        exp_name="${exp}"
        agent_name="${exp_name}-${seed}"
        
        echo "Exp name ${exp_name}"
        eval_exp="eval-${agent_name}"
        yml=${yml_dir}/${eval_exp}.yml
        
        sed -e "s/agent_name/${agent_name}/g" -e "s/algorithm/${algorithm}/g" -e "s/population/${exp_name}/g" -e "s/seed/${seed}/g" "${bias_yml}" > "${yml}"
        
        if [[ $exp == *"mlp" ]]; then
            sed -i -e "s/rnn_policy_config/mlp_policy_config/g" "${yml}"
        fi

        python eval/eval_with_population.py --env_name ${env} --algorithm_name ${algo} --experiment_name "${eval_exp}" --scenario_name "${scenario}" \
        --num_agents ${num_agents} --seed 1 --episode_length 200 --n_eval_rollout_threads $((168 * 10)) --eval_episodes $((168 * 20)) --eval_stochastic --dummy_batch_size 2 \
        --use_proper_time_limits \
        --use_wandb \
        --population_yaml_path "${yml}" --population_size ${population_size} \
        --eval_result_path "eval/results/${scenario}/${algorithm}/${eval_exp}.json" \
        --agent_name "${agent_name}"
    done
done