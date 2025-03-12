#include "pch.h"
#include "MainWindow.xaml.h"
#if __has_include("MainWindow.g.cpp")
#include "MainWindow.g.cpp"
#endif

#include <winrt/Windows.Storage.Pickers.h>
#include <winrt/Windows.Storage.h>
#include <winrt/Windows.Foundation.h>
#include <windows.h> //GetActiveWindow()
#include <shobjidl_core.h> //IInitializeWithWindow
#include <winrt/Microsoft.UI.Dispatching.h> //DispatcherQueue

using namespace winrt;
using namespace Microsoft::UI::Xaml;
using namespace Microsoft::UI::Xaml::Controls;
using namespace Windows::Storage;
using namespace Windows::Storage::Pickers;

namespace winrt::SmartBin::implementation
{
    MainWindow::MainWindow()
    {
        InitializeComponent();
    }

    int32_t MainWindow::MyProperty()
    {
        return 42;
    }

    void MainWindow::MyProperty(int32_t value)
    {
    }

    void MainWindow::myToggle_Click(IInspectable const&, RoutedEventArgs const&)
    {
        if (myToggle().Content().as<winrt::hstring>() == L"Live View")
        {
            myToggle().Content(box_value(L"Upload File"));
        }
        else
        {
            myToggle().Content(box_value(L"Live View"));
        }

        UpdateBorderContent();
    }

    void MainWindow::UpdateBorderContent()
    {
        using namespace winrt::Microsoft::UI;

        if (myToggle().Content().as<winrt::hstring>() == L"Upload File")
        {
            StackPanel panel;
            panel.Orientation(Orientation::Vertical);
            panel.HorizontalAlignment(HorizontalAlignment::Center);
            panel.VerticalAlignment(VerticalAlignment::Center);
            panel.Background(Media::SolidColorBrush(Colors::White()));
            panel.Width(200);
            panel.Height(65);

            TextBlock text;
            text.Text(L"FILE UPLOAD");
            text.Foreground(Media::SolidColorBrush(Colors::Black()));
            text.HorizontalAlignment(HorizontalAlignment::Center);
            panel.Children().Append(text);

            Grid buttonContainer; //for positioning
            buttonContainer.HorizontalAlignment(HorizontalAlignment::Stretch);
            buttonContainer.VerticalAlignment(VerticalAlignment::Stretch);

            Button uploadButton;
            uploadButton.Content(box_value(L"Upload File"));
            uploadButton.Foreground(Media::SolidColorBrush(Colors::LightSkyBlue()));
            uploadButton.HorizontalAlignment(HorizontalAlignment::Center);
            uploadButton.VerticalAlignment(VerticalAlignment::Center);
            uploadButton.Click({ this, &MainWindow::UploadFileButton_Click }); // Attach event handler

            buttonContainer.Children().Append(uploadButton);
            panel.Children().Append(buttonContainer);

            borderControl().Child(panel);
        }
        else
        {
            StackPanel panel;
            panel.Orientation(Orientation::Vertical);
            panel.HorizontalAlignment(HorizontalAlignment::Center);
            panel.VerticalAlignment(VerticalAlignment::Center);
            panel.Background(Media::SolidColorBrush(Colors::Black()));
            panel.Width(1000);
            panel.Height(600);

            borderControl().Child(panel);
        }
    }

    void MainWindow::UploadFileButton_Click(IInspectable const&, RoutedEventArgs const&)
    {
        FileOpenPicker picker;

        //necesary for file picker//////////////////
        auto hwnd = GetActiveWindow();
        winrt::com_ptr<IInitializeWithWindow> initWindow;
        picker.as(initWindow);
        initWindow->Initialize(hwnd);
        ///////////////////////////////////////////

        picker.SuggestedStartLocation(PickerLocationId::DocumentsLibrary);
        picker.FileTypeFilter().Append(L"*");

        //bring up file picker asynchronously
        auto asyncOp = picker.PickSingleFileAsync();

        asyncOp.Completed([this](winrt::Windows::Foundation::IAsyncOperation<StorageFile> const& operation, winrt::Windows::Foundation::AsyncStatus const status)
            {
                if (status == winrt::Windows::Foundation::AsyncStatus::Completed)
                {
                    StorageFile file = operation.GetResults();
                    if (file)
                    {
                        winrt::hstring filePath = file.Path();

                        //update UI display file path
                        winrt::Microsoft::UI::Dispatching::DispatcherQueue::GetForCurrentThread().TryEnqueue(
                            [this, filePath]()
                            {
                                DisplayFilePath(filePath);
                            });
                    }
                }
            });
    }

    void MainWindow::DisplayFilePath(winrt::hstring const& filePath)
    {
        ContentDialog dialog;
        dialog.Title(box_value(L"File Selected"));
        dialog.Content(box_value(filePath));
        dialog.CloseButtonText(L"OK");
        dialog.XamlRoot(borderControl().XamlRoot());
        dialog.ShowAsync();
    }

    void MainWindow::myStatistics_Click(IInspectable const&, RoutedEventArgs const&)
    {
        if (myStatistics().Content().as<winrt::hstring>() == L"Statistics")
        {
            myStatistics().Content(box_value(L"Close Statistics"));

        }
        else
        {
            myStatistics().Content(box_value(L"Statistics"));
        }
        //after each click update drop down panel
        UpdateStatisticsContent();
    }
    void MainWindow::UpdateStatisticsContent()
    {
        using namespace winrt::Microsoft::UI;

        if (myStatistics().Content().as<winrt::hstring>() == L"Statistics")
        {
            StackPanel panel;
            panel.Orientation(Orientation::Vertical);
            panel.HorizontalAlignment(HorizontalAlignment::Center);
            panel.VerticalAlignment(VerticalAlignment::Center);
            panel.Background(Media::SolidColorBrush(Colors::White()));
            panel.Width(1000);
            panel.Height(600);

            TextBlock text;
            text.Text(L"Statistics");
            text.Foreground(Media::SolidColorBrush(Colors::Black()));
            text.HorizontalAlignment(HorizontalAlignment::Center);
            panel.Children().Append(text);

            borderControl().Child(panel);
        }
        else
        {
            StackPanel panel;
            panel.Orientation(Orientation::Vertical);
            panel.HorizontalAlignment(HorizontalAlignment::Center);
            panel.VerticalAlignment(VerticalAlignment::Center);
            panel.Background(Media::SolidColorBrush(Colors::Black()));
            panel.Width(1000);
            panel.Height(600);

            borderControl().Child(panel);

        }
    }
}