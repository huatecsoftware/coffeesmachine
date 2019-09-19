import {  requestPOST } from '../utils/request'

const host = window.location.hostname
const port = '8888'

export function queryOrder(param) {
  return requestPOST(`http://${host}:${port}/queryAllOrder/`,param)
}
export function rangeClick(param) {
  return requestPOST(`http://${host}:${port}/rangeClick/`,param)
}
export function addOrder(param) {
  return requestPOST(`http://${host}:${port}/addOrder/`, param)
}
export function PLCON(param) {
  return requestPOST(`http://${host}:${port}/PLCON/`, param)
}
export function PLCOFF(param) {
  return requestPOST(`http://${host}:${port}/PLCOFF/`, param)
}
export function searchOrderByVal(param) {
  return requestPOST(`http://${host}:${port}/searchOrder/`, param)
}
export function intelligenceModel(param) {
  return requestPOST(`http://${host}:${port}/intelligenceModel/`, param)
}
export function loopDB(param) {
  return requestPOST(`http://${host}:${port}/loopDB/`, param)
}
export function logClear(param) {
  return requestPOST(`http://${host}:${port}/logClear/`, param)
}
export function failOrder(param) {
  return requestPOST(`http://${host}:${port}/failOrder/`, param)
}
export function logRcv(param) {
  return requestPOST(`http://${host}:${port}/logRcv/`, param)
}
export function addCheck(param) {
  return requestPOST(`http://${host}:${port}/addCheck/`, param)
}
export function addUser(param) {
  return requestPOST(`http://${host}:${port}/addUser/`, param)
}
export function deleteTempFile(param) {
  return requestPOST(`http://${host}:${port}/deleteTempFile/`, param)
}
export function photograph(param) {
  return requestPOST(`http://${host}:${port}/photograph/`, param)
}
