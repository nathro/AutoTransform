package autotransform.input;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;

/**
 * Unit test for directory input.
 */
class DirectoryInputTest {

    private static final String C_TEST_DATA_DIR = "C:\\repos\\autotransform\\src\\test\\java\\autotransform\\input\\data\\";

    /**
     * Tests that the getFiles function returns expected results.
     */
    @Test
    void testGetFiles() {
        DirectoryInput input = new DirectoryInput(C_TEST_DATA_DIR + "emptyDirectory");
        assertArrayEquals(new String[0], input.getFiles().toArray());
        input = new DirectoryInput(C_TEST_DATA_DIR + "nonEmptyDirectory");
        assertArrayEquals(new String[]{C_TEST_DATA_DIR + "nonEmptyDirectory\\test.txt"}, input.getFiles().toArray());
    }

}
