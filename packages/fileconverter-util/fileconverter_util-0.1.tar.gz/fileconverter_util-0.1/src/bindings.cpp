#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <regex>
namespace py = pybind11;
std::string line_csv_to_json(const std::string& line) {
    std::stringstream ss(line);
    std::string item;
    std::vector<std::pair<std::string, std::string>> kv_pairs;

    while (std::getline(ss, item, ',')) {
        auto pos = item.find('=');
        if (pos != std::string::npos) {
            std::string key = item.substr(0, pos);
            std::string value = item.substr(pos + 1);
            kv_pairs.emplace_back(key, value);
        }
    }

    std::stringstream json_ss;
    json_ss << "{";
    for (size_t i = 0; i < kv_pairs.size(); ++i) {
        json_ss << "\"" << kv_pairs[i].first << "\": \"" << kv_pairs[i].second << "\"";
        if (i + 1 < kv_pairs.size()) {
            json_ss << ", ";
        }
    }
    json_ss << "}";
    return json_ss.str();
}
std::vector<std::string> csv_file_to_json(const std::string& filepath){
    std::ifstream file(filepath);
    std::string line;
    std::vector<std::string> lines;
    std::vector<std::string> json_lines;
    if(!file.is_open()){
        throw std::runtime_error("Could not open file: " + filepath);
    }
    while(std::getline(file, line)){
        json_lines.push_back(line_csv_to_json(line));
    }
    return json_lines;
}
std::vector<std::string> csv_lines_to_json(std::vector<std::string> lines){
    std::vector<std::string> json_lines;
    for(const auto& line : lines){
        json_lines.push_back(line_csv_to_json(line));
    }
    return json_lines;
}

std::vector<std::string> md_to_html(const std::vector<std::string>& lines) {
    std::vector<std::string> html_lines;
    bool in_list = false;

    for (const auto& line : lines) {
        std::string html_line = line;
        if (line.starts_with("# ")) {
            html_line = "<h1>" + line.substr(2) + "</h1>";
        } else if (line.starts_with("## ")) {
            html_line = "<h2>" + line.substr(3) + "</h2>";
        } else if (line.starts_with("### ")) {
            html_line = "<h3>" + line.substr(4) + "</h3>";
        } else if (line.starts_with("#### ")){
            html_line = "<h4>" + line.substr(5) + "</h4>";
        } else if (line.starts_with("##### ")){
            html_line = "<h5>" + line.substr(6) + "</h5>";
        } else if (line.starts_with("###### ")){
            html_line = "<h6>" + line.substr(7) + "</h6>";
        }

        else if (line.starts_with("- ")) {
            if (!in_list) {
                html_lines.push_back("<ul>");
                in_list = true;
            }
            html_line = "<li>" + line.substr(2) + "</li>";
        } else {
            if (in_list) {
                html_lines.push_back("</ul>");
                in_list = false;
            }
        }
        html_line = std::regex_replace(html_line, std::regex(R"(\*\*(.*?)\*\*)"), "<strong>$1</strong>");
        html_line = std::regex_replace(html_line, std::regex(R"(__([^_]+)__)"), "<strong>$1</strong>");
        html_line = std::regex_replace(html_line, std::regex(R"(\*(.*?)\*)"), "<em>$1</em>");
        html_line = std::regex_replace(html_line, std::regex(R"(_([^_]+)_)"), "<em>$1</em>");
        html_line = std::regex_replace(html_line, std::regex(R"(`([^`]+)`)"), "<code>$1</code>");
        if (!html_line.empty() &&
            html_line.find("<h") != 0 &&
            html_line.find("<ul>") != 0 &&
            html_line.find("</ul>") != 0 &&
            html_line.find("<li>") != 0 &&
            html_line.find("<p>") != 0 &&
            html_line.find("<code>") != 0
        ) {
            html_line = "<p>" + html_line + "</p>";
        }

        html_lines.push_back(html_line);
    }
    if (in_list) {
        html_lines.push_back("</ul>");
    }

    return html_lines;
}
PYBIND11_MODULE(fileconverter_util, m){
    m.def("md_to_html", &md_to_html, "Convert Markdown lines to HTML lines. Returns an array of lines.");
    m.def("csv_lines_to_json", &csv_lines_to_json, "Convert CSV lines to JSON lines. Returns an array of lines.");
    m.def("csv_file_to_json", &csv_file_to_json, "Convert a CSV file to JSON. Returns an array of lines.");
}