package autotransform.input;

import java.util.Vector;

import com.google.gson.Gson;

/*
 * Inputs are used by A
 */
public abstract class Input {
    
    abstract public Vector<String> getFiles();

    public static Input get(InputType type, String data) throws EnumConstantNotPresentException {
        Gson gson = new Gson();
        switch (type) {
            case DIRECTORY:
                return gson.fromJson(data, DirectoryInput.class);
            default:
                throw new UnsupportedOperationException();
        }
    }
}
