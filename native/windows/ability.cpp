// Copyright 2026 InsightOS
// SPDX-License-Identifier: Apache-2.0
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <shellapi.h>
#include <filesystem>
#include <iostream>
#include <string>
#include <vector>

std::wstring quote(const std::wstring& value) {
    std::wstring result=L"\""; size_t backslashes=0;
    for(auto c:value) {
        if(c==L'\\') {++backslashes;continue;}
        if(c==L'"') result.append(backslashes*2+1,L'\\');
        else result.append(backslashes,L'\\');
        result+=c;backslashes=0;
    }
    result.append(backslashes*2,L'\\');return result+L'"';
}
struct Handle {
    HANDLE value=nullptr;
    ~Handle(){if(value&&value!=INVALID_HANDLE_VALUE) CloseHandle(value);}
};
int failed(const char* operation) {
    auto error=GetLastError();std::cerr<<operation<<" failed: "<<error<<'\n';return 1;
}
int wmain(int argc,wchar_t** argv) {
    wchar_t executable[32768];
    auto count=GetModuleFileNameW(nullptr,executable,32768);
    if(!count||count>=32768)return failed("Locate Ability");
    auto root=std::filesystem::path(executable).parent_path().parent_path();
    auto main=root/L"main.py";
    if(!std::filesystem::is_regular_file(main)){std::cerr<<"Missing Ability main.py\n";return 1;}
    auto length=GetEnvironmentVariableW(L"SEMANTIC_ABILITY_PYTHON",nullptr,0);
    if(!length){std::cerr<<"SEMANTIC_ABILITY_PYTHON must select the bundled Python\n";return 1;}
    std::wstring python(length,L'\0');GetEnvironmentVariableW(L"SEMANTIC_ABILITY_PYTHON",python.data(),length);python.resize(length-1);
    if(!std::filesystem::path(python).is_absolute()||!std::filesystem::is_regular_file(python)){
        std::cerr<<"SEMANTIC_ABILITY_PYTHON must be an absolute executable path\n";return 1;
    }
    if(!SetEnvironmentVariableW(L"ABILITY_ROOT",root.c_str()))return failed("Set Ability root");
    std::wstring command=quote(python)+L" "+quote(main.wstring());
    for(int i=1;i<argc;++i)command+=L" "+quote(argv[i]);
    Handle job{CreateJobObjectW(nullptr,nullptr)};
    if(!job.value)return failed("Create Ability job");
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};
    // This launcher only owns its Python child. It mirrors Linux parent-death
    // cleanup; the supervisor's enclosing Robot job deliberately does not use
    // KILL_ON_JOB_CLOSE and preserves Ability processes on unconfirmed stop.
    limits.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if(!SetInformationJobObject(job.value,JobObjectExtendedLimitInformation,&limits,sizeof(limits)))return failed("Set Ability job policy");
    SIZE_T bytes=0;InitializeProcThreadAttributeList(nullptr,1,0,&bytes);
    std::vector<unsigned char> storage(bytes);
    auto attributes=reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(storage.data());
    if(!InitializeProcThreadAttributeList(attributes,1,0,&bytes))return failed("Initialize process attributes");
    if(!UpdateProcThreadAttribute(attributes,0,PROC_THREAD_ATTRIBUTE_JOB_LIST,&job.value,sizeof(job.value),nullptr,nullptr)){
        auto result=failed("Assign Ability job attribute");DeleteProcThreadAttributeList(attributes);return result;
    }
    STARTUPINFOEXW startup{};startup.StartupInfo.cb=sizeof(startup);startup.lpAttributeList=attributes;
    PROCESS_INFORMATION process{};
    BOOL started=CreateProcessW(python.c_str(),command.data(),nullptr,nullptr,TRUE,
        EXTENDED_STARTUPINFO_PRESENT|CREATE_UNICODE_ENVIRONMENT,nullptr,nullptr,&startup.StartupInfo,&process);
    auto createError=GetLastError();DeleteProcThreadAttributeList(attributes);
    if(!started){SetLastError(createError);return failed("Start Ability Python");}
    Handle child{process.hProcess},thread{process.hThread};
    if(WaitForSingleObject(child.value,INFINITE)!=WAIT_OBJECT_0)return failed("Wait for Ability Python");
    DWORD exitCode=1;if(!GetExitCodeProcess(child.value,&exitCode))return failed("Read Ability exit status");
    return static_cast<int>(exitCode);
}
