#pragma once

#include "MainWindow.g.h"
#include <winrt/Windows.Storage.Pickers.h>
#include <winrt/Windows.Storage.h>
#include <winrt/Windows.Foundation.h>
#include <windows.h> 
#include <shobjidl_core.h> 
#include <winrt/Microsoft.UI.Xaml.Controls.h>

namespace winrt::SmartBin::implementation
{
    struct MainWindow : MainWindowT<MainWindow>
    {
        MainWindow();

        int32_t MyProperty();
        void MyProperty(int32_t value);

        void myToggle_Click(IInspectable const& sender, Microsoft::UI::Xaml::RoutedEventArgs const& args);
        void UpdateBorderContent();
        void UploadFileButton_Click(IInspectable const& sender, Microsoft::UI::Xaml::RoutedEventArgs const& args);
        void DisplayFilePath(winrt::hstring const& filePath);
        void myStatistics_Click(IInspectable const& sender, Microsoft::UI::Xaml::RoutedEventArgs const& args);
        void UpdateStatisticsContent();
    };
}

namespace winrt::SmartBin::factory_implementation
{
    struct MainWindow : MainWindowT<MainWindow, implementation::MainWindow>
    {
    };
}
