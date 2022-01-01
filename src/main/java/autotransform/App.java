package autotransform;

import autotransform.input.DirectoryInput;
/**
 * Hello world!
 */
public final class App {
    /**
     *
     */
    private static final String C_APP_DIRECTORY = "C:/repos/autotransform/src/";

    /**
     * Says hello to the world.
     * @param args The arguments of the program.
     */
    public static void main(String[] args) {
        DirectoryInput input = new DirectoryInput(C_APP_DIRECTORY);
        for (String path : input.getFiles()) {
            System.out.println(path);
        }
    }
}
