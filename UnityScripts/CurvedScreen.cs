using UnityEngine;

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class CurvedScreen : MonoBehaviour
{
    public float radius = 10f; // Distance from camera
    public float height = 5f;  // Height of the screen
    public float angleDegrees = 180f; // Curve amount (180 is a half-circle in front of you)
    public int segments = 32;  // Smoothness of the curve

    void Start()
    {
        Mesh mesh = new Mesh();
        mesh.name = "CurvedScreen";

        Vector3[] vertices = new Vector3[(segments + 1) * 2];
        Vector2[] uvs = new Vector2[(segments + 1) * 2];
        int[] triangles = new int[segments * 6];

        float halfAngle = angleDegrees / 2f;
        float angleStep = angleDegrees / segments;

        for (int i = 0; i <= segments; i++)
        {
            // Calculate curved positions
            float currentAngle = -halfAngle + (i * angleStep);
            float rad = currentAngle * Mathf.Deg2Rad;
            float x = Mathf.Sin(rad) * radius;
            float z = Mathf.Cos(rad) * radius;

            // Bottom vertex
            vertices[i] = new Vector3(x, -height / 2f, z);
            uvs[i] = new Vector2((float)i / segments, 0f);

            // Top vertex
            vertices[i + segments + 1] = new Vector3(x, height / 2f, z);
            uvs[i + segments + 1] = new Vector2((float)i / segments, 1f);
        }

        int t = 0;
        for (int i = 0; i < segments; i++)
        {
            int bottom = i;
            int top = i + segments + 1;

            // Create the rectangular faces
            triangles[t++] = bottom;
            triangles[t++] = top;
            triangles[t++] = bottom + 1;

            triangles[t++] = bottom + 1;
            triangles[t++] = top;
            triangles[t++] = top + 1;
        }

        mesh.vertices = vertices;
        mesh.uv = uvs;
        mesh.triangles = triangles;
        mesh.RecalculateNormals(); // Fix lighting

        GetComponent<MeshFilter>().mesh = mesh;
    }
}
