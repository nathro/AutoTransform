package autotransform.input;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Vector;
import java.util.stream.Stream;

public class DirectoryInput extends Input {
    private String path;

    public DirectoryInput(String path) {
        this.path = path;
    }

    @Override
    public Vector<String> getFiles() {
        try {
            Stream<Path> paths = Files.walk(Paths.get(this.path)).filter(Files::isRegularFile);
            return new Vector<String>(paths.map(Path::toAbsolutePath).map(Path::toString).toList());
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }
}
