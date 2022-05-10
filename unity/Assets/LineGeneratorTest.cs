using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

public class TrackLayout
{
    public string name{get;set;}
    public Dictionary<string, Dictionary<string, object>> lines{get;set;}
    public Dictionary<string, Dictionary<string, object>> junctions{get;set;}
}

public class LineGeneratorTest : MonoBehaviour
{
    [SerializeField] private LineController mainLineThing;

    [SerializeField] private GameObject linePrefab;
    [SerializeField] private GameObject junctionPrefab;

    private TrackLayout layoutData;

    private Dictionary<string, LineController> lines = new Dictionary<string, LineController>();
    private Dictionary<string, JunctionController> junctions = new Dictionary<string, JunctionController>();

    void Awake()
    {
        TextAsset layout_file = Resources.Load("TrackLayouts/sample_line") as TextAsset;
        layoutData = JsonConvert.DeserializeObject<TrackLayout>(layout_file.text);
        Debug.Log("Importing Layout: "+layoutData.name);
        //LoadLines();
        //line.SetupLine(points);
    }

    void Update()
    {
        Debug.Log("Information on J2: "+ junctions["J2"]);
    }

    // Start is called before the first frame update
    void Start()
    {
        LoadLines();
        LoadJunctions();
    }

    private void LoadLines()
    {
        int count = 0;
        foreach(var (linename, line) in layoutData.lines){
            List<Vector2> nodes = new List<Vector2>();
            foreach(object node_data in line["nodes"] as IEnumerable){
                float[] node_coords = {0, 0};
                int i = 0;
                foreach(object term in node_data as IEnumerable){
                    node_coords[i] = float.Parse(term.ToString());
                    i++;
                }
                Vector2 node = new Vector2(node_coords[0], node_coords[1]);
                nodes.Add(Vector2.Scale(node, new Vector2(0.8f, -0.8f)) + new Vector2(-8f,4f));
            }
            GameObject clone = Instantiate(linePrefab, new Vector3(0,0,0), Quaternion.identity);
            lines[linename] = clone.GetComponent<LineController>();
            lines[linename].SetupLine(nodes.ToArray());
        }

    }

    private void LoadJunctions()
    {
        foreach(var (junction_name, junction) in layoutData.junctions){
            float[] junction_coords = {0, 0};
            int i = 0;
            foreach(object term in junction["position"] as IEnumerable){
                junction_coords[i] = float.Parse(term.ToString());
                i++;
            }
            Debug.Log("Setting up junction: "+junction_name);
            Vector2 junction_pos = new Vector2(junction_coords[0], junction_coords[1]);
            junction_pos = Vector2.Scale(junction_pos, new Vector2(0.8f, -0.8f)) + new Vector2(-8f,4f);

            if((string) junction["type"] == "StandardPoints"){
                LineController startline = lines[(string) junction["startline"]];
                LineController mainline = lines[(string) junction["mainline"]];
                LineController branchline = lines[(string) junction["branchline"]];

                GameObject junction_clone = Instantiate(junctionPrefab, new Vector3(0,0,0), Quaternion.identity);
                junctions[junction_name] = junction_clone.GetComponent<JunctionController>();
                junctions[junction_name].Setup(junction_pos,startline,mainline,branchline);
            }else{
                //throw new NotImplementedException("Junction type "+ junction["type"] +" is not implemented.");
            }
        }
    }

}
