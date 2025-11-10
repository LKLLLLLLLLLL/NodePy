import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Visitor from '@/views/Visitor.vue'
import Home from '@/views/Home.vue'
import File from '@/views//FileListView/File.vue'
import Project from '@/views/ProjectListView/ProjectList.vue'
import Login_Register from '@/views/Login_Register.vue'
import Example from '@/views/Example.vue'
import Editor from '@/views/Editor.vue'

// 定义路由类型
const routes: Array<RouteRecordRaw> = [
    {
        path:'/',
        redirect:'/home'
    },
    {
        path: '/visitor',
        name: 'visitor',
        component: Visitor
    },
    {
        path: '/home',
        name: 'home',
        component: Home
    },
    {
        path: '/file',
        name: 'file',
        component: File
    },
    {
        path: '/project',
        name: 'project',
        component: Project
    },
    {
        path: '/login_register',
        name: 'login_register',
        component: Login_Register
    },
    {
        path: '/example',
        name: 'example',
        component: Example
    },
    {
        path: '/editor/:projectId',
        name: 'editor',
        component: Editor
    }
]

const router = createRouter({
    history: createWebHistory('/'),
    routes
})

export default router
