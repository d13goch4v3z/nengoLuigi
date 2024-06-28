#include <iostream>
#include <cmath>
#include <vector>

int main() {
    const int array_size = 100;
    std::vector<int> array(array_size, 0); // Initialize array with zeros

    const double scale = 10.0; // Scale factor for the sine wave
    const double shift = array_size / 2.0; // Shift to center the sine wave in the array

    // Generate sinusoidal positions and place 1s
    for (int i = 0; i < array_size; ++i) {
        // Calculate sinusoidal index (scaled and shifted)
        int index = static_cast<int>(std::sin(i / scale) * shift + shift);
        
        // Ensure the index is within bounds
        if (index >= 0 && index < array_size) {
            array[index] = 1;
        }
    }

    // Print the array
    for (int i = 0; i < array_size; ++i) {
        std::cout << array[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}