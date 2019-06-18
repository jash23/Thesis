from pyomo.environ import *
from pyomo.core import Var

model = AbstractModel()

model.K = Set()  # set of components
model.P = Set()  # set of processes
model.C = Set()  # set of individual ratio checks
model.T = Set()  # set of transferring components
model.N = Set()  # set of plants
model.V = Set()  # set of decision_two constraints
model.sparse_f = Set(model.C, dimen=2)
model.sparse_g = Set(model.C, dimen=2)
model.sparse_e = Set(model.K)
model.sparse_h = Set(model.K)
model.sparse_o = Set(model.N, dimen=2)
model.sparse_q = Set(model.V, dimen=2)
model.sparse_j = Set(model.K)
model.KP = Set(dimen=2)
model.X = Var(model.KP)
model.I = Var(model.K, within=NonNegativeReals, initialize=0)
model.S = Var(model.N, within=NonNegativeReals)
model.Q = Var(model.K, within=NonNegativeReals, initialize=0)
model.b = Var(model.N, within=Boolean)
model.e = Param(model.K, model.P, default=0)
model.h = Param(model.K, model.P, default=0)
model.j = Param(model.K, model.P, default=0)
model.i = Param(model.K, default=0)
model.a = Param(model.K, default=0)
model.r_x = Param(model.K, model.P, model.C, default=0)
model.r_y = Param(model.K, model.P, model.C, default=0)
model.f = Param(model.K, model.P, model.C, default=0)
model.g = Param(model.K, model.P, model.C, default=0)
model.d = Param(model.K, default=0)
model.l = Param(model.K, default=0)
model.u = Param(model.P, default=0)
model.o = Param(model.K, model.P, model.N, default=0)
model.r = Param(model.K, model.P, default=0)
model.q = Param(model.K, model.N, model.V, default=0)
model.Q_max = Param(model.K, default=0)
model.s = Param(model.K, default=0)

def objective_rule(model):
    #print(sum(model.a[k] * model.X[k, p] if model.a[k] != 0 else 0 for k,p in model.j.sparse_iterkeys()) + sum(model.a[k] * model.i[k] * model.I[k] for k in model.a.sparse_iterkeys()) + sum(model.a[k] * model.s[k] * model.Q[k] for k in model.a.iterkeys()))
    return sum(model.a[k] * model.X[k, p] if model.a[k] != 0 else 0 for k,p in model.j.sparse_iterkeys()) + sum(model.a[k] * model.i[k] * model.I[k] for k in model.a.sparse_iterkeys()) + sum(model.a[k] * model.s[k] * model.Q[k] for k in model.a.iterkeys())
    # return sum(sum(model.j[k, p] * model.a[k] * model.X[k, p] if model.j[k, p] != 0 else 0 for p in model.P) + model.i[k] * model.a[k] * model.I[k] + model.s[k] * model.a[k] * model.Q[k] if model.a[k] != 0 else 0 for k in model.K)
model.obj = Objective(rule=objective_rule, sense=maximize)

def detect_sparsity_f(model):
    for k,p,c in model.f.sparse_iterkeys():
        #print(model.sparse_f[k,c].add(p))
        model.sparse_f[c].add((k,p))
model.detect_sparsity_f = BuildAction(rule=detect_sparsity_f)

def detect_sparsity_g(model):
    for k,p,c in model.g.sparse_iterkeys():
        # print(model.sparse_g[k,c].add(p))
        model.sparse_g[c].add((k, p))
model.detect_sparcity_g = BuildAction(rule=detect_sparsity_g)

def ratio_check(model, c):
    return sum((model.f[k, p, c] * model.X[k, p]) / model.r_x[k, p, c] for k, p in model.sparse_f[c]) == sum((model.g[k, p, c] * model.X[k, p]) / model.r_y[k, p, c] for k, p in model.sparse_g[c])
    # return sum(sum((model.f[k, p, c] * model.X[k, p]) / model.r_x[k, p, c] if model.f[k, p, c] != 0 else 0 for k in model.Kf)for p in model.Pf) == sum(sum((model.g[k, p, c] * model.X[k, p]) / model.r_y[k, p, c] if model.g[k, p, c] != 0 else 0 for k in model.Kg)for p in model.Pg)
    # print(sum(sum(model.f[k, p, c]*model.X[k, p] for k in model.K)for p in model.P)/sum(sum(model.f[k, p, c]*model.r_x[k, p, c] for k in model.K)for p in model.P) == sum(sum(model.g[k, p, c]*model.X[k, p] for k in model.K)for p in model.P)/sum(sum(model.g[k, p, c]*model.r_y[k, p, c] for k in model.K)for p in model.P))
    # return sum(sum(model.f[k, p, c] * model.X[k, p] for k in model.K) for p in model.P) / sum(sum(model.f[k, p, c] * model.r_x[k, p, c] for k in model.K) for p in model.P) == sum(sum(model.g[k, p, c] * model.X[k, p] for k in model.K) for p in model.P) / sum(sum(model.g[k, p, c] * model.r_y[k, p, c] for k in model.K) for p in model.P)
model.ratio_check = Constraint(model.C, rule=ratio_check)

def detect_sparsity_j(model):
    for k,p in model.j.sparse_iterkeys():
        model.sparse_j[k].add(p)
model.detect_sparsity_j = BuildAction(rule=detect_sparsity_j)

def demand_end(model, k):
    if k not in model.sparse_j:
        return Constraint.Skip
    else:
        return sum(model.j[k, p]*model.X[k, p] for p in model.sparse_j[k]) + model.Q[k] <= max(model.l[k]*model.d[k], 0)
model.demand_end = Constraint(model.K, rule=demand_end)

def demand_middle(model, k):
    if model.i[k] == 0:
        return Constraint.Skip
    #print(model.i[k]*model.I[k] <= max(model.i[k]*model.d[k], 0))
    return model.i[k]*model.I[k] <= max(model.i[k]*model.d[k], 0)
model.demand_middle = Constraint(model.K, rule=demand_middle)

def detect_sparsity_e(model):
    for k,p in model.e.sparse_iterkeys():
        model.sparse_e[k].add(p)
model.detect_sparsity_e = BuildAction(rule=detect_sparsity_e)

def detect_sparsity_h(model):
     for k,p in model.h.sparse_iterkeys():
         model.sparse_h[k].add(p)
model.detect_sparsity_h = BuildAction(rule=detect_sparsity_h)

def mass_balance(model, k):
    #print(sum(model.e[k, p]*model.X[k, p] for p in model.sparse_e[k]) == sum(model.h[k, p]*(model.X[k, p]) for p in model.sparse_h[k])+(model.i[k]*model.I[k]))
    return sum(model.e[k, p]*model.X[k, p] for p in model.sparse_e[k]) + model.Q[k] == sum(model.h[k, p]*(-model.X[k, p]) for p in model.sparse_h[k])+(model.i[k]*model.I[k])
model.mass_balance = Constraint(model.T, rule=mass_balance)

def detect_sparsity_o(model):
    for k,p,m in model.o.sparse_iterkeys():
        #print(model.sparse_f[k,c].add(p))
        model.sparse_o[m].add((k,p))
model.detect_sparsity_o = BuildAction(rule=detect_sparsity_o)

def plant_capacity(model, m):
    # print(sum(sum(model.o[k, p, m] * model.X[k, p] / model.u[p] for k in model.K) for p in model.P) + model.S[m] == 1)
    return sum(model.o[k, p, m] * model.X[k, p] / model.u[p] for k,p in model.sparse_o[m]) + model.S[m] == 1
model.plant_capacity = Constraint(model.N, rule=plant_capacity)

def decision_one(model, m):
    # print(model.S[m] <= 1 - model.b[m])
    return model.S[m] <= 1 - model.b[m]
model.decision_one = Constraint(model.N, rule=decision_one)

def detect_sparsity_q(model):
    for k,m,v in model.q.sparse_iterkeys():
        #print(model.sparse_f[k,c].add(p))
        model.sparse_q[v].add((k,m))
model.detect_sparsity_q = BuildAction(rule=detect_sparsity_q)

def decision_two(model, v):
    # print(sum(sum(model.q[k, m, v] * (model.Q[k] <= model.Q_max[k] * model.b[m]) for m in model.N) for k in model.K))
    return sum(model.q[k, m, v] * (model.Q[k] <= model.Q_max[k] * model.b[m]) for k,m in model.sparse_q[v])
model.decision_two = Constraint(model.V, rule=decision_two)

def x_const(model, k, p):
    if model.r[k,p] > 0:
        #print(model.X[k,p] >= 0)
        return model.X[k,p] >= 0
    else:
        # print(model.X[k,p] <=0)
        return model.X[k,p] <=0
model.x_const = Constraint(model.KP, rule=x_const)

# instance = model.create_instance("optimizer.dat")
# solver = SolverFactory('glpk')
# # # solver_opt = dict()
# # # solver_opt['log'] = 'recipe_test.log'
# results = solver.solve(instance)
# instance.solutions.load_from(results)
# # print(value(instance.Q[10608407]))
# # print(instance.demand_end[10608407].body.to_string())
# # print(value(instance.demand_end[10608407].body))
#
# with open('labels2.csv', 'w') as r:
#     r.write("component, process, value\n")
#     for k,p in instance.KP:
#         r.write("%f,%s,%f\n" % (k,p,instance.X[k,p].value))
#     for k in instance.i.sparse_iterkeys():
#         r.write("%f,,%f\n" % (k,instance.I[k].value))