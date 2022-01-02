package autotransform.input;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.fail;

import java.net.URISyntaxException;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.junit.jupiter.api.Test;

/**
 * Unit test for directory input.
 */
class DirectoryInputTest {

    private static final String C_TEST_DATA_DIR = "\\test-classes\\autotransform\\input\\data\\";

    /**
     * Tests that the getFiles function returns expected results.
     */
    @Test
    void testGetFiles() {
        Path targetPath;
        try {
            targetPath = Paths.get(getClass().getResource("/").toURI()).getParent();
        } catch (URISyntaxException e1) {
            fail("Unable to find target path");
            return;
        }
        DirectoryInput input = new DirectoryInput(targetPath + C_TEST_DATA_DIR + "emptyDirectory");
        assertArrayEquals(new String[0], input.getFiles().toArray());
        input = new DirectoryInput(targetPath + C_TEST_DATA_DIR + "nonEmptyDirectory");
        assertArrayEquals(new String[]{targetPath + C_TEST_DATA_DIR + "nonEmptyDirectory\\test.txt"}, input.getFiles().toArray());
    }

}
