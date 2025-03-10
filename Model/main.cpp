
#include<opencv2/opencv.hpp>
#include<opencv2/imgproc.hpp>
#include<opencv2/dnn.hpp>
#include<opencv2/highgui.hpp>

#include<iostream>
#include<fstream>

using namespace cv;
using namespace dnn;
using namespace std;

const float SCORE_THRESHOLD = 0.5;
const float NMS_THRESHOLD = 0.5;
const Size2f model_Shape(Size(640, 640));
vector<string> classes;

vector<string> get_classes()
{
    vector<string> classes;
    ifstream ifs("C:\\Users\\edg\\Downloads\\coco-classes.txt");
    string line;
    while (getline(ifs, line))
    {
        classes.push_back(line);
    }
    return classes;
}

void load_net(Net& net, bool is_cuda)
{
    auto result = readNetFromONNX("C:\\Users\\edg\\Desktop\\Projects\\yolov8n.onnx");
    if (is_cuda)
    {
        result.setPreferableBackend(DNN_BACKEND_CUDA);
        result.setPreferableTarget(DNN_TARGET_CUDA);
    }
    else
    {
        result.setPreferableBackend(DNN_BACKEND_OPENCV);
        result.setPreferableTarget(DNN_TARGET_CPU);
    }
    net = result;
}
void detect(Mat& image, Net& net)
{
    Mat modelInput = image;

    Mat blob;
    blobFromImage(modelInput, blob, 1 / 255.0, model_Shape, Scalar(0, 0, 0), true, false);
    net.setInput(blob);

    vector<Mat> outputs;
    net.forward(outputs, net.getUnconnectedOutLayersNames());

    int rows = outputs[0].size[1];
    int cols = outputs[0].size[2];

    rows = outputs[0].size[2];
    cols = outputs[0].size[1];

    outputs[0] = outputs[0].reshape(1, cols);
    transpose(outputs[0], outputs[0]);

    float* data = (float*)outputs[0].data;

    vector<int> classIds;
    vector<float> confidences;
    vector<Rect2d> boxes;

    for (int i = 0; i < rows; i++)
    {

        float* classes_score = data + 4;

        Mat scores(1, 80, CV_32FC1, classes_score);
        Point classId;
        double maxClassScore;

        cv::minMaxLoc(scores, 0, &maxClassScore, 0, &classId);

        if (maxClassScore > SCORE_THRESHOLD)
        {

            confidences.push_back(maxClassScore);
            classIds.push_back(classId.x);
            cout << classId.x << endl;

            float x = data[0];  // center x 
            float y = data[1];    // center y
            float w = data[2];    // width
            float h = data[3];    // height

            int left = x * modelInput.cols - w * modelInput.cols / 2;
            int top = y * modelInput.rows - h * modelInput.rows / 2;

            int width = w * modelInput.cols;
            int height = h * modelInput.rows;

            boxes.push_back(Rect2d(left, top, width, height));

        }
        data += cols;
    }
    vector<int> nms_result;
    NMSBoxes(boxes, confidences, SCORE_THRESHOLD, NMS_THRESHOLD, nms_result);


    for (unsigned long i = 0; i < nms_result.size(); ++i)
    {
        int idx = nms_result[i];
        Point center(boxes[idx].x + boxes[idx].width / 2, boxes[idx].y + boxes[idx].height / 2);
        Point topLeft(boxes[idx].x, boxes[idx].y);
        Point bottomRight(boxes[idx].x + boxes[idx].width, boxes[idx].y + boxes[idx].height);
        cout << boxes[idx] << endl;
        /*rectangle(modelInput, boxes[idx], Scalar(0, 200, 255));*/
        cv::rectangle(modelInput, topLeft, bottomRight, Scalar(0, 255, 0), 3);
        putText(modelInput, to_string(int(confidences[idx] * 100)) + "%" + classes[classIds[idx]], Point(boxes[idx].x, boxes[idx].y), 1, 3, Scalar(0, 200, 255), 2);
    }

}


int main() {

    //string path = "C:\\Users\\edg\\Documents\\GitHub\\TACO\\data\\batch_1\\000003.jpg";
    //Mat img = imread(path);
    //imshow("Image", img);
    //waitKey(0);

    //return 0;
    classes = get_classes();

    //string path = "C:\\Users\\Edgar\\Downloads\\bottle.jpg";
    Mat frame;
    VideoCapture capture(0);

    Net net;
    load_net(net, false);


    while (true)
    {
        capture.read(frame);
        detect(frame, net);

        imshow("output", frame);

        if (waitKey(1) != -1)
        {
            capture.release();
            break;
        }

    }
    return 0;

}
