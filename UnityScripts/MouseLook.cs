using UnityEngine;

public class MouseLook : MonoBehaviour
{
    public float mouseSensitivity = 300f;
    float xRotation = 0f;
    float yRotation = 0f;

    void Start()
    {
        // Lock the cursor to the center of the game window
        Cursor.lockState = CursorLockMode.Locked;
    }

    void Update()
    {
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity * Time.deltaTime;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity * Time.deltaTime;

        xRotation -= mouseY;
        xRotation = Mathf.Clamp(xRotation, -90f, 90f);
        
        yRotation += mouseX;

        // Rotate the camera based on mouse movement
        transform.localRotation = Quaternion.Euler(xRotation, yRotation, 0f);
    }
}
