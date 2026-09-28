from action_sequences import action_sequences
assert action_sequences([(10,11.5)],[],30)==[]
assert action_sequences([(10,11.5)],[(9,10)],30)
assert len(action_sequences([(10,12),(13,15),(16,18)],[],30))==1
assert action_sequences([(10,12),(20,22)],[],30)==[]
assert action_sequences([(0,5)],[],5)==[(0,5)] or action_sequences([(0,5)],[],5)==[[0,5]]
from automatic_cut import select_ranges
t=[dict(words=[dict(text=' Hello.',start=10,end=11)])]
k,_,_=select_ranges(t,[(9,12)],30)
assert any(a<=10 and b>=11 for a,b in k)
print('PASS: isolated gunfire dropped, sustained sequences joined, commentary action preserved')
