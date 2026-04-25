
#include <stdio.h> // Necessary for printf
#include <stdlib.h> // Same for srand, rand, atoi
#include <time.h> //  To measure time

double elapsed_ms(struct timespec start, struct timespec end) {
    double seconds = (double)(end.tv_sec - start.tv_sec); // time elapsed in seconds
    double nanoseconds = (double)(end.tv_nsec - start.tv_nsec); // time elapsed in nanoseconds
    return seconds * 1000.0 + nanoseconds / 1000000.0; // Conversion en millisecondes
}

int main(int argc, char **argv) { // argc : amount of arguments, argv : arguments given to the code
    int samples = 50;     // Number of measures
    int repeat = 1000000; // Number of multiplications for each measures

    if (argc >= 2) samples = atoi(argv[1]); // atoi convert str to int
    if (argc >= 3) repeat = atoi(argv[2]);

    srand(1234); // Random number generator initializer

    // Important to avoid results stacking.
    volatile unsigned long long sink = 0;

    for (int s = 0; s < samples; s++) {
        struct timespec start, end;

        clock_gettime(CLOCK_MONOTONIC, &start); // Start the clock

        for (int i = 0; i < repeat; i++) { // Repeat samples* the operation
            unsigned long long a = rand() % 1000000000000ULL; // ~10^12
            unsigned long long b = rand() % 1000000000000ULL;

            sink += a * b; // Put into the volatile variable -> The variable comes back to 0 for each iteration and don't stack them
        }

        clock_gettime(CLOCK_MONOTONIC, &end); // End the clock

        printf("%.6f\n", elapsed_ms(start, end));
    }

    return 0;
}

