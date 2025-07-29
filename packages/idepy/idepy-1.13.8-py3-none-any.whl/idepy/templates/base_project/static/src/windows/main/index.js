const {createApp, ref, watch} = Vue
// 创建当前页面数据实例
const app = createApp({
    setup() {
        // Vue3变量创建
        const rData = ref({
            version: "",
        })

        // 配置项
        const config = ref({})

        // 通过接口刷新当前程序配置项
        function refreshConfigData() {
            pywebview.api.get_config_data().then((data) => {
                console.log("[Config]", data)
                config.value = data
            })
        }


        // 通过接口程序刷新当前页面数据
        function refreshData() {
            pywebview.api.get_data().then((data) => {
                console.log("[data]", data)
                rData.value = data
            })
        }


        // 通过接口数据将当前页面数据传递到Python
        function updateData() {
            pywebview.api.set_data(rData?.value)
        }

        // 获取api对象
        const api = ref({})
        const api_interval = setInterval(()=>{
            if (window?.pywebview?.api){
                clearInterval(api_interval)
                api.value = window?.pywebview?.api;
            }
        }, 333)

        // 暴露相关方法、变量，提供Vue访问
        return {
            rData, refreshData, updateData,
            config,refreshConfigData,
            api,
            window:window,

        }
    }
})

// 挂载element-plus组件库
app.use(ElementPlus, {
    locale: ElementPlusLocaleZhCn
});

// 创建Vue实例
const vm = app.mount('#app')


// 挂载常用方法到全局变量
window.refreshData = vm.refreshData
window.refreshConfigData = vm.refreshConfigData
window.updateData = vm.updateData


// 窗口创建完毕后将调用逻辑
window.addEventListener('pywebviewready', () => {
    console.log("[INFO]桌面应用初始化成功")

    // 获取初始数据
    vm.refreshData()
    vm.refreshConfigData()
})


// 测试按钮逻辑
function buttonTest() {
    // 调用python声明的api
    api.btn_click('IDEPY被点击').then((data) => {
        // python响应的数据返回
        console.log("[Python Response]", data)

        // 使用elementPlus弹出消息框
        ElementPlus?.ElMessageBox?.alert(
            `${data?.msg}`,
            'Python响应内容',
            {
                dangerouslyUseHTMLString: true,
            }
        )


        // 其他逻辑...
    })
}
