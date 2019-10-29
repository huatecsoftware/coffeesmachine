import { requestPOST } from '../utils/request'

const host = window.location.hostname
const port = '8888'

export function queryOrder(param) {
  return requestPOST(`http://${host}:${port}/queryAllOrder/`, param)
}
export function rangeClick(param) {
  return requestPOST(`http://${host}:${port}/rangeClick/`, param)
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
export function addUser(param) {
  return requestPOST(`http://${host}:${port}/addUser/`, param)
}
export function deleteTempFile(param) {
  return requestPOST(`http://${host}:${port}/deleteTempFile/`, param)
}
export function photograph(param) {
  return requestPOST(`http://${host}:${port}/photograph/`, param)
}
export function AIState(param) {
  return requestPOST(`http://${host}:${port}/AIState/`, param)
}
export function calcFaceEncoding(param) {
  return requestPOST(`http://${host}:${port}/calcFaceEncoding/`, param)
}
export function savePerson(param) {
  return requestPOST(`http://${host}:${port}/savePerson/`, param)
}
