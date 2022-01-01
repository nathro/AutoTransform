package autotransform.input;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;

import org.junit.jupiter.api.Test;

/**
 * Unit test for CachedFile.
 */
public class CachedFileTest {
    private static final String C_TEST_FILE = "C:\\repos\\autotransform\\src\\test\\java\\autotransform\\input\\data\\CachedFileTestData";
    private static final String C_TEST_FILE_CONTENT = "Just some text\nThat is a test";

    /**
     * Tests that the getContent function returns expected results.
     */
    @Test
    void testGetFiles() {
        CachedFile file = new CachedFile(C_TEST_FILE);
        try {
            assertEquals(C_TEST_FILE_CONTENT, file.getContent());
        } catch (IOException e) {
            fail("Cached file threw exception: " + e.toString());
        }
    }
}
