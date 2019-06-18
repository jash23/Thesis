from pyomo.environ import *
from pyomo.dae import *

m = ConcreteModel()

K = ['1', '2', '3', '4']
P = ['p1', 'p2', 'p3']
C = ['c1', 'c2', 'c3']
T = ['2']
m.t = ContinuousSet(bounds=(0, 10))
a = {'3': 10, '4': 20}
r_x = {('2', 'p1', 'c1'): 1, ('3', 'p2', 'c2'): 2, ('4', 'p3', 'c3'): 2}
r_y = {('1', 'p1', 'c1'): 2, ('2', 'p2', 'c2'): 1, ('2', 'p3', 'c3'): 1}
f = {('2', 'p1', 'c1'): 1, ('3', 'p2', 'c2'): 1}
g = {('1', 'p1', 'c1'): 1, ('2', 'p2', 'c2'): 1}
j = {('3', 'p2'): 1}
e = {('2', 'p1'): 1, ('3', 'p2'): 1}
h = {('1', 'p1'): 1, ('2', 'p2'): 1}
s = {'2': 10}
m.d = Var(K, m.t, within=NonNegativeReals)
m.d_end = Var(K, m.t)
m.d_end_dt = DerivativeVar(m.d_end, withrespectto=m.t)
m.Y = Var(K, m.t, within=NonNegativeReals)
m.dydt = DerivativeVar(m.Y, withrespectto=m.t)
m.X = Var(K, P, m.t, within=NonNegativeReals)
m.dXdt = DerivativeVar(m.X, withrespectto=m.t)

def objective_rule(m):
    return a['3'] * m.d_end['3', m.t.last()] + a['4'] * m.d_end['4', m.t.last()]
m.obj = Objective(rule=objective_rule, sense=maximize)

def ratio1(m, t):
    return m.X['2', 'p1', t]/r_x['2', 'p1', 'c1'] == m.X['1', 'p1', t]/r_y['1', 'p1', 'c1']
m.ratio1 = Constraint(m.t, rule=ratio1)

def ratio2(m, t):
    return m.X['3', 'p2', t]/r_x['3', 'p2', 'c2'] == m.X['2', 'p2', t]/r_y['2', 'p2', 'c2']
m.ratio2 = Constraint(m.t, rule=ratio2)

def ratio3(m, t):
    return m.X['4', 'p3', t]/r_x['4', 'p3', 'c3'] == m.X['2', 'p3', t]/r_y['2', 'p3', 'c3']
m.ratio3 = Constraint(m.t, rule=ratio3)

# def demand_init(m):
#     return m.dvar['3', m.t.first()] == 0
# m.demand_condition1 = Constraint(rule=demand_init)

# def demand_final(m):
#     return m.d['3', m.t.last()] <= 100
# m.demand_condition2 = Constraint(rule=demand_final)

def demand(m, t):
    return m.X['3', 'p2', t] == m.d['3', t]
m.demand = Constraint(m.t, rule=demand)

def demand2(m, t):
    return m.X['4', 'p3', t] == m.d['4', t]
m.demand2 = Constraint(m.t, rule=demand2)

def max_demand(m):
    return m.d_end['3', m.t.last()] <= 100
m.max_demand1 = Constraint(rule=max_demand)

def max_demand2(m):
    return m.d_end['4', m.t.last()] <= 100
m.max_demand2 = Constraint(rule=max_demand2)

def d_der(m, t):
    return m.d_end_dt['3', t] == m.d['3', t]
m.d_der1 = Constraint(m.t, rule=d_der)

def d_der2(m, t):
    return m.d_end_dt['4', t] == m.d['4', t]
m.d_der2 = Constraint(m.t, rule=d_der2)

def stock(m, t):
    return m.dydt['2',t] == m.X['2','p1',t] - m.X['2','p2',t] + m.X['2', 'p3', t]
m.stock = Constraint(m.t, rule=stock)

def init(m,k):
    return m.d_end[k, m.t.first()] == 0
m.initial_cond = Constraint(K, rule=init)

def init_stock(m):
    return m.Y['2', m.t.first()] == 10
m.initial_stock = Constraint(rule=init_stock)

def stock_consumption(m, t):
    return m.X['2', 'p1', t] + m.Y['2', t] == m.X['2', 'p2', t] + m.X['2', 'p3', t]
m.stock_should_be_consumed = Constraint(m.t, rule=stock_consumption)

def cap(m, t):
    return m.X['2', 'p1', t]/10 <= 1
m.cap1 = Constraint(m.t, rule=cap)

def cap2(m, t):
    return m.X['3', 'p2', t]/10 + m.X['4', 'p3', t]/20 <= 1
m.cap2 = Constraint(m.t, rule=cap2)

# def X_ode(m, t):
#     return m.dXdt['2','p1',t] <= 10
# m.diff_X = Constraint(m.t, rule=X_ode)

# def X_ode2(m, t):
#     return m.dXdt['3', 'p2', t] <= 10
# m.diff_X2 = Constraint(m.t, rule=X_ode2)
#
# def X_ode3(m, t):
#     return m.dXdt['4', 'p3', t] <= 20
# m.diff_x3 = Constraint(m.t, rule=X_ode3)

# def capa(m, t):
#     return m.dXdt['3', 'p2', t]/10 + m.dXdt['4', 'p3', t]/10 <= 1
# m.capacity = Constraint(m.t, rule=capa)


#
# def capacity1(m, t):
#     return m.X['2', 'p1', t]/100 <= 1
# m.cap1 = Constraint(m.t, rule=capacity1)
#
# def capacity2(m, t):
#     return m.X['3', 'p2', t]/100 <= 1
# m.cap2 = Constraint(m.t, rule=capacity2)

discretizer = TransformationFactory('dae.finite_difference')
discretizer.apply_to(m, nfe=10, wrt=m.t, scheme='BACKWARD')
# solver = SolverFactory('glpk')
# solver.solve(m, tee=True)
# instance.m.pprint()