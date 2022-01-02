package autotransform.input;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.junit.jupiter.api.Test;

/**
 * Unit test for CachedFile.
 */
public class CachedFileTest {
    private static final String C_TEST_FILE = "/test-classes/autotransform/input/data/CachedFileTestData";
    private static final String C_TEST_FILE_CONTENT = "Just some text\nThat is a test";

    /**
     * Tests that the getContent function returns expected results.
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

        CachedFile file = new CachedFile(targetPath.toString() + C_TEST_FILE);
        try {
            assertEquals(C_TEST_FILE_CONTENT, file.getContent());
        } catch (IOException e) {
            fail("Cached file threw exception: " + e.toString());
        }
    }
}
