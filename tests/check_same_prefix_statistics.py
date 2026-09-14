"""Detect future-split leakage, reference-tie errors, and erased negative H."""
from src.methods.same_prefix_statistics import root_statistics


def main():
    reversal=root_statistics([[0,0],[1,1]],[[1,1],[0,0]])
    assert reversal['selected']==1 and reversal['g']==-1 and reversal['h']<0
    tie=root_statistics([[1,0],[0,1]],[[0,0],[1,1]])
    assert tie['selected']==0 and tie['g']==0
    fallback=root_statistics([[1,0]],[[0,1]])
    assert fallback['h'] is None and fallback['g']==0
    print('PASS: selection uses A only, ties retain reference, negative H survives, and single-candidate fallback is defined.')

if __name__=='__main__':
    main()
