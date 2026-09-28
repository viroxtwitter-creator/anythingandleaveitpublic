"""Group acoustic events before selection; isolated gunshots are not a scene."""
from review_core import merge_intervals

def action_sequences(events,speech,duration):
    raw=merge_intervals(events,0,duration)
    groups=[]
    for a,b in raw:
        if groups and a-groups[-1][-1][1]<=1.25:groups[-1].append((a,b))
        else:groups.append([(a,b)])
    result=[]
    for group in groups:
        a,b=group[0][0],group[-1][1]
        supported=any(x<=b+1.0 and y>=a-1.0 for x,y in speech)
        active=sum(y-x for x,y in group)
        # Commentary-associated action remains; standalone action needs sustained
        # evidence. This is a heuristic, not visual understanding of a fight.
        if supported or active>=4.0:
            result.append([max(0,a-.45),min(duration,b+.65)])
    return merge_intervals(result,0,duration)
