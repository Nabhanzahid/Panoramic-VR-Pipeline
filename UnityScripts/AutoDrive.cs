using UnityEngine;

public class AutoDrive : MonoBehaviour
{
    public float speed = 10f;
    
    void Update()
    {
        // Moves the rig forward continuously
        transform.Translate(Vector3.forward * speed * Time.deltaTime);
    }
}
