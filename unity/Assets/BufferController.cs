using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BufferController : MonoBehaviour
{

    private LineController connectingline;
    private Vector2 position;
    public bool autogenerated; // Is true if the buffer was auto-generated

    public void Setup(Vector2 position, LineController connectingline, bool visible=false, bool autogenerated=false) {
        gameObject.transform.position = position;
        GetComponent<MeshRenderer>().enabled = visible;

        this.position = position;
        this.connectingline = connectingline;
        this.visible = visible;
        this.autogenerated = autogenerated;
    }

    public override string ToString() {
        return "B"+position;
    }

    // Update is called once per frame
    void Update()
    {

    }
}