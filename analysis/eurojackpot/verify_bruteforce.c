/*
 * INDEPENDENT CHECK #2 - full brute force, different language, different method.
 *
 * Enumerates every single one of the C(50,5) * C(12,2) = 139,838,160 possible
 * Eurojackpot outcomes explicitly (five nested loops over the main numbers,
 * two nested loops over the euro numbers) and counts, for two concrete
 * tickets, how many outcomes fall in each event of interest.
 *
 * No combinatorics library, no probability formulas - just counting.
 *
 *   gcc -O2 -o verify_bruteforce verify_bruteforce.c && ./verify_bruteforce
 */

#include <stdio.h>
#include <stdint.h>

/* The two concrete tickets analysed in REPORT.md */
static const int T1_MAIN[5] = {33, 38, 42, 47, 50};
static const int T1_EURO[2] = {5, 11};
static const int T2_MAIN[5] = {34, 36, 43, 45, 49};
static const int T2_EURO[2] = {8, 12};

/* paying[k][j] = 1 if k main + j euro matches is one of the 12 prize tiers */
static int paying[6][3];

static void init_paying(void) {
    int tiers[12][2] = {{5,2},{5,1},{5,0},{4,2},{4,1},{3,2},
                        {4,0},{2,2},{3,1},{3,0},{1,2},{2,1}};
    for (int i = 0; i < 12; i++) paying[tiers[i][0]][tiers[i][1]] = 1;
}

int main(void) {
    init_paying();

    uint64_t t1m = 0, t1e = 0, t2m = 0, t2e = 0;
    for (int i = 0; i < 5; i++) { t1m |= 1ULL << T1_MAIN[i]; t2m |= 1ULL << T2_MAIN[i]; }
    for (int i = 0; i < 2; i++) { t1e |= 1ULL << T1_EURO[i]; t2e |= 1ULL << T2_EURO[i]; }

    if (t1m & t2m) { printf("ERROR: main numbers overlap\n"); return 1; }
    if (t1e & t2e) { printf("ERROR: euro pairs overlap\n"); return 1; }

    /* Pre-compute the 66 euro draws: match counts for each ticket. */
    int euro_m1[66], euro_m2[66], n_euro = 0;
    for (int a = 1; a <= 12; a++)
        for (int b = a + 1; b <= 12; b++) {
            uint64_t d = (1ULL << a) | (1ULL << b);
            euro_m1[n_euro] = __builtin_popcountll(d & t1e);
            euro_m2[n_euro] = __builtin_popcountll(d & t2e);
            n_euro++;
        }

    uint64_t total = 0, w_union = 0, w_both = 0, w_ge4 = 0, w_42 = 0, w_t1_any = 0;
    uint64_t tier_t1[6][3] = {{0}};

    for (int a = 1; a <= 50; a++)
    for (int b = a + 1; b <= 50; b++)
    for (int c = b + 1; c <= 50; c++)
    for (int d = c + 1; d <= 50; d++)
    for (int e = d + 1; e <= 50; e++) {
        uint64_t md = (1ULL << a) | (1ULL << b) | (1ULL << c)
                    | (1ULL << d) | (1ULL << e);
        int m1 = __builtin_popcountll(md & t1m);
        int m2 = __builtin_popcountll(md & t2m);

        for (int k = 0; k < n_euro; k++) {
            int e1 = euro_m1[k], e2 = euro_m2[k];
            int p1 = paying[m1][e1], p2 = paying[m2][e2];

            total++;
            if (p1 || p2) w_union++;
            if (p1 && p2) w_both++;
            if (m1 >= 4 || m2 >= 4) w_ge4++;
            if ((m1 == 4 && e1 == 2) || (m2 == 4 && e2 == 2)) w_42++;
            if (p1) { w_t1_any++; tier_t1[m1][e1]++; }
        }
    }

    printf("outcomes enumerated      : %llu\n", (unsigned long long)total);
    printf("\n--- BRUTE-FORCE COUNTS (numerators over %llu) ---\n",
           (unsigned long long)total);
    printf("any prize, one ticket    : %llu\n", (unsigned long long)w_t1_any);
    printf("any prize, two tickets   : %llu\n", (unsigned long long)w_union);
    printf("both tickets win         : %llu\n", (unsigned long long)w_both);
    printf(">=4 main, two tickets    : %llu\n", (unsigned long long)w_ge4);
    printf("4+2, two tickets         : %llu\n", (unsigned long long)w_42);

    printf("\n--- AS PROBABILITIES ---\n");
    printf("any prize, one ticket    : %.9f%%\n", 100.0 * w_t1_any / total);
    printf("any prize, two tickets   : %.9f%%\n", 100.0 * w_union / total);
    printf("both tickets win         : %.9f%%\n", 100.0 * w_both / total);
    printf(">=4 main, two tickets    : %.9f%%\n", 100.0 * w_ge4 / total);
    printf("4+2, two tickets         : %.9f%%\n", 100.0 * w_42 / total);

    printf("\n--- per-tier outcome counts, ticket 1 ---\n");
    for (int k = 5; k >= 0; k--)
        for (int j = 2; j >= 0; j--)
            if (paying[k][j])
                printf("  %d+%d: %10llu\n", k, j, (unsigned long long)tier_t1[k][j]);

    return 0;
}
