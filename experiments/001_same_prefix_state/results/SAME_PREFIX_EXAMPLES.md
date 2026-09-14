# Raw same-prefix development examples

These are the earliest accepted F and M development roots at the locked eta=0.03.
Selection does not use future outcomes. Exact IDs, source paths, and proposal
measurements are retained in [the compact JSON](same_prefix_examples_v1.json).

## F: root 0 (Norfolk_Island)

Shared generated prefix for the reference and alternative:

```text
 1,779 square kilometres (3,710 sq mi). Norfolk Island is
```

All emitted token IDs match. Raw block symmetric KL sum is 0.00010854564
(maximum position 5.3476153e-05); latent displacement is 0.463731
and displacement after BF16 conversion is 0.456825.
There are 16 free generated positions; known prompt latents remain equal.

The first archived A noise gives these 32-token suffixes:

Reference:

```text
 one of the most populated islands on the Island of Maltes, and the island are the largest island in the country. Norfolk Island was named in the 1
```

Alternative:

```text
 one of the most populated islands on the Island of Malpin, and the island are the largest island in the country. Norfolk Island was named in the 1
```

This illustration shows one coupled realization. Distribution evidence comes
from the independent A/B estimator across the full fixed cohort.

## M: root 1 (Party_leaders_of_the_United_States_House_of_Representatives)

Shared generated prefix for the reference and alternative:

```text
 If the Minority Leader is elected the Majority Leader or Majority Leader, the
```

All emitted token IDs match. Raw block symmetric KL sum is 1.4664717e-05
(maximum position 6.7758669e-06); latent displacement is 0.318137
and displacement after BF16 conversion is 0.319207.
There are 14 free generated positions; known prompt latents remain equal.

