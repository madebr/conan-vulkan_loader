#include <vulkan/vulkan.h>

#include <stdio.h>

const VkApplicationInfo appInfo = {
    .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
    .pApplicationName = "Vulkan Headers Test Package",
    .applicationVersion = VK_MAKE_VERSION(1, 0, 0),
    .pEngineName = "No Engine",
    .engineVersion = VK_MAKE_VERSION(1, 0, 0),
    .apiVersion = VK_API_VERSION_1_0,
};

const VkInstanceCreateInfo createInfo = {
    .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
    .pApplicationInfo = &appInfo,
    .enabledExtensionCount = 0,
};

VkInstance instance = VK_NULL_HANDLE;

int vulkan_init()
{
    VkResult result = vkCreateInstance(&createInfo, 0, &instance);
    fflush(stdout);
    return result == VK_SUCCESS;
}

void vulkan_destroy()
{
    vkDestroyInstance(instance, 0);
}

int main()
{
    vulkan_init();
    vulkan_destroy();
}