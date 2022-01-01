package autotransform;

import java.io.File;
import java.util.Scanner;

/**
 * Hello world!
 */
public final class App {
    /**
     *
     */
    private static final String C_APP_FILE = "C:/repos/autotransform/src/main/java/autotransform/App.java";

    /**
     * Says hello to the world.
     * @param args The arguments of the program.
     */
    public static void main(String[] args) {
        File testFile = new File(C_APP_FILE);
        if (testFile.canRead()) {
            try {
                Scanner reader = new Scanner(testFile);
                while (reader.hasNextLine()) {
                    System.out.println(reader.nextLine());
                }
                reader.close();
            } catch (Exception E) {

            }
        } else {
            System.out.println("Failure");
        }
        System.out.println("Hello World!");
    }
}
