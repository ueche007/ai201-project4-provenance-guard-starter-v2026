# Calibration run

- Produced by: `calibrate.py::main` from `calibration/texts.json`
- Weights model 0.6 / style 0.4, veto below 0.5, thresholds human < 0.45, AI > 0.7
- Tuned on these same texts, so this shows the settings fit, not that they generalise.

| ID | Kind | Source | Perplexity | Sentence spread | Vocabulary (MATTR) | Punct /100w | model | style | combined | guess |
|---|---|---|---|---|---|---|---|---|---|---|
| ai_1 | ai | AI-generated for this calibration set | 21.6 | 0.347 | 0.943 | 0.00 | 0.764 | 0.798 | 0.777 | ai |
| ai_2 | ai | AI-generated for this calibration set | 7.4 | 0.243 | 0.878 | 0.00 | 0.947 | 0.882 | 0.921 | ai |
| ai_3 | ai | AI-generated for this calibration set | 10.7 | 0.303 | 0.820 | 0.00 | 0.908 | 0.767 | 0.852 | ai |
| ai_4 | ai | AI-generated for this calibration set | 13.7 | 0.323 | 0.877 | 0.67 | 0.870 | 0.776 | 0.833 | ai |
| ai_5 | ai_plain | AI-generated for this calibration set | 12.5 | 0.302 | 0.714 | 0.00 | 0.886 | 0.680 | 0.804 | ai |
| ai_6 | ai_plain | AI-generated for this calibration set | 12.0 | 0.274 | 0.803 | 0.00 | 0.892 | 0.774 | 0.845 | ai |
| ai_7 | ai_edited | AI-generated for this calibration set | 53.0 | 0.415 | 0.925 | 0.00 | 0.435 | 0.674 | 0.531 | unsure |
| ai_8 | ai_edited | AI-generated for this calibration set | 17.2 | 0.397 | 0.866 | 4.81 | 0.823 | 0.497 | 0.690 | unsure |
| human_1 | human_public_domain | Doyle, Sherlock Holmes | 47.4 | 0.828 | 0.851 | 7.02 | 0.479 | 0.141 | 0.344 | human |
| human_2 | human_public_domain | Doyle, Sherlock Holmes | 33.7 | 0.737 | 0.800 | 4.31 | 0.614 | 0.091 | 0.404 | human |
| human_3 | human_public_domain | Thoreau, Walden | 87.8 | 0.822 | 0.812 | 2.29 | 0.256 | 0.143 | 0.210 | human |
| human_4 | human_public_domain | Thoreau, Walden | 79.7 | 1.053 | 0.821 | 5.86 | 0.286 | 0.102 | 0.212 | human |
| human_5 | human_public_domain | Twain, Life on the Mississippi | 57.2 | 0.840 | 0.810 | 5.82 | 0.405 | 0.091 | 0.280 | human |
| human_6 | human_public_domain | Twain, Life on the Mississippi | 41.1 | 0.685 | 0.782 | 3.61 | 0.536 | 0.086 | 0.356 | human |
| human_7 | human_public_domain | Grimm, Fairy Tales | 25.1 | 0.780 | 0.768 | 10.09 | 0.719 | 0.049 | 0.451 | unsure |
| human_8 | human_public_domain | Grimm, Fairy Tales | 23.3 | 0.703 | 0.772 | 7.43 | 0.741 | 0.063 | 0.470 | unsure |
| human_9 | human_public_domain | Jerome, Three Men in a Boat | 38.5 | 0.797 | 0.781 | 9.70 | 0.562 | 0.060 | 0.361 | human |
| human_10 | human_public_domain | Jerome, Three Men in a Boat | 33.7 | 0.448 | 0.830 | 2.02 | 0.614 | 0.425 | 0.538 | unsure |
| human_11 | human_public_domain | Montgomery, Anne of Green Gables | 41.7 | 0.815 | 0.844 | 10.00 | 0.530 | 0.134 | 0.372 | human |
| human_12 | human_public_domain | Montgomery, Anne of Green Gables | 33.6 | 0.655 | 0.819 | 13.37 | 0.615 | 0.129 | 0.421 | human |
| human_13 | human_public_domain | Baum, Wizard of Oz | 22.3 | 0.609 | 0.802 | 6.57 | 0.755 | 0.129 | 0.505 | unsure |
| human_14 | human_public_domain | Baum, Wizard of Oz | 30.9 | 0.495 | 0.755 | 2.50 | 0.646 | 0.241 | 0.484 | unsure |
| human_15 | human_public_domain | Twain, Huckleberry Finn | 96.4 | 0.828 | 0.776 | 6.12 | 0.228 | 0.054 | 0.158 | human |
| human_16 | human_public_domain | Twain, Huckleberry Finn | 45.5 | 0.451 | 0.743 | 13.14 | 0.495 | 0.268 | 0.405 | human |

## Summary

| Group | human | unsure | ai | mean combined | range |
|---|---|---|---|---|---|
| human | 11 | 5 | 0 | 0.373 | 0.158 – 0.538 |
| ai | 0 | 2 | 6 | 0.782 | 0.531 – 0.921 |
