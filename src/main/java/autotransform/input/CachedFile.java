package autotransform.input;

import java.io.File;
import java.io.IOException;
import java.util.Scanner;

public class CachedFile {
    private String path;
    private String content;

    public CachedFile(String path) {
        this.path = path;
    }

    public String getContent() throws IOException {
        if (this.content == null) {
            File file = new File(this.path);
            Scanner scanner = new Scanner(file);
            StringBuilder builder = new StringBuilder();
            if (scanner.hasNext()) {
                builder.append(scanner.nextLine());
            }
            while (scanner.hasNext()) {
                builder.append("\n");
                builder.append(scanner.nextLine());
            }
            scanner.close();
            this.content = builder.toString();
        }

        return this.content;
    }

    public String getPath() {
        return this.path;
    }
}
